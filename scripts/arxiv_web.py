#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arxiv_web.py - 从 arXiv 网页补全元数据（v1.3）

为什么不用 arXiv API：本机出口 IP 对 /api/query 长期返回 429（限流），
但 arxiv.org/abs/<id> 与 arxiv.org/html/<id> 页面可正常访问。
因此改为解析网页：

  - abs 页  -> 标题 / 作者 / 日期 / **Comments（含 CVPR、Oral、Highlight 等）** / Subjects
  - html 页 -> 作者脚注里的**所属机构**（论文正文首页）

结果缓存 data/arxivweb_cache.json（默认 14 天），失败不阻塞主管道。
"""
from __future__ import annotations

import datetime
import json
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor

import net

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(ROOT, "data")
CACHE_PATH = os.path.join(DATA_DIR, "arxivweb_cache.json")
CACHE_TTL_DAYS = 14

_lock = threading.Lock()
_ABS_RE = re.compile(
    r'<td class="tablecell label">Comments:</td>\s*<td class="tablecell comments[^"]*">(.*?)</td>',
    re.S,
)
_SUBJ_RE = re.compile(
    r'<td class="tablecell label">Subjects:</td>\s*<td[^>]*>(.*?)</td>', re.S
)
_JREF_RE = re.compile(
    r'<td class="tablecell label">Journal\s*ref:</td>\s*<td[^>]*>(.*?)</td>', re.S
)
_TITLE_RE = re.compile(r'<meta[^>]+name="citation_title"[^>]+content="([^"]*)"', re.I)
_AUTH_RE = re.compile(r'<meta[^>]+name="citation_author"[^>]+content="([^"]*)"', re.I)
_DATE_RE = re.compile(r'<meta[^>]+name="citation_date"[^>]+content="([^"]*)"', re.I)

# 机构识别线索词（与 paper_meta 一致，放宽以覆盖企业实验室）
INST_HINT = re.compile(
    r"University|Universit|Institute|Institut|College|Laborator|Corporation|Inc\b|Ltd|"
    r"Research|Academy|Center|Centre|School|Lab\b|Tech\b|Meta|Google|Microsoft|"
    r"ByteDance|Tencent|Alibaba|Baidu|Huawei|DeepSeek|NVIDIA|Apple|Amazon|Adobe|"
    r"Tsinghua|Peking|Shanghai|Zhejiang|Fudan|SJTU|MIT|Stanford|Berkeley|CMU|"
    r"Oxford|Cambridge|ETH|EPFL|KAUST|NUS|NTU|HKUST|CUHK|INRIA|Max Planck",
    re.I,
)


def _strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", s).strip()


def load_cache() -> dict:
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:  # noqa: BLE001
            return {}
    return {}


def save_cache(cache: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)
    os.replace(tmp, CACHE_PATH)


def _fresh(rec: dict) -> bool:
    try:
        ts = datetime.datetime.fromisoformat(rec.get("_ts", ""))
        return (datetime.datetime.now() - ts).days < CACHE_TTL_DAYS
    except Exception:  # noqa: BLE001
        return False


def fetch_abs(arxiv_id: str, timeout: int = 30) -> dict:
    """抓 arXiv 摘要页，返回 {title, authors, date, comment, subjects, journal_ref}。"""
    url = f"https://arxiv.org/abs/{arxiv_id}"
    html = net.get_text(url, timeout=timeout, retries=1)
    out: dict = {}
    m = _TITLE_RE.search(html)
    if m:
        out["title"] = _strip_tags(m.group(1))
    authors = _AUTH_RE.findall(html)
    if authors:
        out["authors"] = "、".join(_strip_tags(a) for a in authors[:6])
        out["author_count"] = len(authors)
    m = _DATE_RE.search(html)
    if m:
        out["date"] = _strip_tags(m.group(1))
    m = _ABS_RE.search(html)
    if m:
        out["comment"] = _strip_tags(m.group(1))[:300]
    m = _SUBJ_RE.search(html)
    if m:
        out["subjects"] = _strip_tags(m.group(1))[:200]
    m = _JREF_RE.search(html)
    if m:
        out["journal_ref"] = _strip_tags(m.group(1))[:200]
    return out


def _first_text_line(seg: str) -> str:
    """从一段 HTML 中取第一行有意义的文本。"""
    txt = re.sub(r"<[^>]+>", "\n", seg)
    for line in txt.split("\n"):
        line = line.strip(" ,;·\u00a0")
        if 2 < len(line) < 130 and "@" not in line and not line.lower().startswith("http"):
            if line.lower().startswith("affiliation:"):
                line = line.split(":", 1)[1].strip()
            if line:
                return line
    return ""


def fetch_affiliations(arxiv_id: str, timeout: int = 30) -> list[str]:
    """从 arXiv HTML 全文首页提取作者机构（最多 3 个）。

    覆盖三种常见版式：
      A. LaTeXML 新模板：<span class="ltx_contact ltx_role_affiliation"><span class="ltx_contact_name">Affiliation: </span>INST</span>
      B. 1line 作者行：机构直接跟在 ltx_role_affiliation 后
      C. 传统 \thanks 脚注：<p class="ltx_p">1]Inst A 2]Inst B</p> / "address: INST"
    """
    try:
        t = net.get_text(f"https://arxiv.org/html/{arxiv_id}", timeout=timeout, retries=0)
    except Exception:  # noqa: BLE001
        return []
    if len(t) < 20000 or "ltx_personname" not in t:
        return []
    head = t[:120000]

    insts: list[str] = []
    seen: set[str] = set()

    def push(txt: str) -> None:
        txt = txt.strip(" ,;·\u00a0")
        if not (2 < len(txt) < 130):
            return
        key = txt.lower()
        if key not in seen:
            seen.add(key)
            insts.append(txt)

    # A/B：author notes 中的 affiliation 块
    for chunk in head.split('ltx_role_affiliation">')[1:]:
        push(_first_text_line(chunk[:400]))

    # C：传统脚注 / 1] 编号排版
    if len(insts) < 2:
        paras = re.findall(r'<p [^>]*class="ltx_p[^"]*"[^>]*>(.*?)</p>', head, re.S)
        for fn in re.findall(r'<div id="fn[^"]*"[^>]*>(.*?)</div>', head, re.S):
            paras.append(fn)
        for p_ in paras[:12]:
            raw = _strip_tags(p_)
            segs = re.split(r"\s*\d+\]\s*", raw) if re.search(r"\d\]", raw) else [raw]
            if "address:" in raw.lower():
                m_ = re.search(r"address:\s*(.+)", raw, re.I | re.S)
                if m_:
                    segs = [m_.group(1)] + segs
            for seg in segs:
                seg = seg.strip(" ,;·")
                if "@" not in seg and INST_HINT.search(seg):
                    push(seg)
            if len(insts) >= 3:
                break

    return insts[:3]


def enrich_meta(arxiv_ids: list[str], want_affiliations: bool = True,
                workers: int = 5) -> dict:
    """并发补全多条论文元数据，返回 {arxiv_id: {...}}。带磁盘缓存。"""
    cache = load_cache()
    todo = []
    for aid in arxiv_ids:
        rec = cache.get(aid)
        need_aff = want_affiliations and rec is not None and "institutions" not in (rec or {})
        if rec and _fresh(rec) and not need_aff:
            continue
        todo.append(aid)

    if todo:
        def work(aid: str) -> tuple[str, dict]:
            rec = dict(cache.get(aid) or {})
            try:
                rec.update(fetch_abs(aid))
            except Exception as e:  # noqa: BLE001
                rec.setdefault("_abs_error", type(e).__name__)
            if want_affiliations and "institutions" not in rec:
                affs = fetch_affiliations(aid)
                rec["institutions"] = affs
            rec["_ts"] = datetime.datetime.now().isoformat(timespec="seconds")
            return aid, rec

        with ThreadPoolExecutor(max_workers=workers) as ex:
            for aid, rec in ex.map(work, todo):
                with _lock:
                    cache[aid] = rec
        save_cache(cache)

    return {aid: cache.get(aid) or {} for aid in arxiv_ids}


if __name__ == "__main__":
    import sys
    ids = sys.argv[1:] or ["2609.11115"]
    res = enrich_meta(ids, want_affiliations=True)
    for k, v in res.items():
        print(f"=== {k} ===")
        for kk in ("title", "date", "comment", "journal_ref", "subjects", "institutions"):
            if v.get(kk):
                print(f"  {kk}: {str(v[kk])[:150]}")
