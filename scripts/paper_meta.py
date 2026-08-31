#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
paper_meta.py - 论文元数据补全（v0.9）

封面展示需求（用户 2026-08-31）：
  - 作者 + 高校（OpenAlex authorships）
  - 被引数（OpenAlex cited_by_count）
  - GitHub star 数（api.github.com，未鉴权 60/h，仅对入选精选的论文查，带磁盘缓存）

输出缓存：data/meta_cache.json（{arxiv_id: {...}}），失败不阻塞主管道。
"""
import datetime
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(ROOT, "data")
CACHE_PATH = os.path.join(DATA_DIR, "meta_cache.json")
CACHE_TTL_DAYS = 3  # star/被引缓存 3 天


def http_json(url, timeout=25, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "paper-daily/0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "paper-daily/0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")


INST_HINT = re.compile(
    r"University|Institute|College|Laboratory|Corporation|Inc\b|Research|Academy|"
    r"Center|Centre|Dept|School|Lab\b|Meta|Google|Microsoft|ByteDance|Tencent|"
    r"Alibaba|Baidu|Huawei|DeepSeek|NVIDIA|Apple|Amazon|ShanghaiTech|Tsinghua|Peking|MIT|Stanford",
    re.I,
)


def fetch_arxiv_affiliations(arxiv_id):
    """从 arXiv HTML 全文作者脚注块提取单位（arXiv 摘要页已不展示单位，但 HTML 论文首屏脚注有）。
    返回最多 3 个去重单位；无 HTML 版或解析失败返回 []。"""
    try:
        t = _http_get(f"https://arxiv.org/html/{arxiv_id}", timeout=20)
    except Exception:  # noqa: BLE001
        return []
    if len(t) < 20000 or "ltx_personname" not in t:
        return []
    # 兼容多种首屏单位排版：ltx_align_bottom 脚注 / ltx_noindent 首段 1]编号 / footnote address: 块
    paras = re.findall(r'<p [^>]*class="ltx_p[^"]*"[^>]*>(.*?)</p>', t[:80000], re.S)
    # footnote 块（address: 风格）整体并入候选段
    for fn in re.findall(r'<div id="fn[^"]*"[^>]*>(.*?)</div>', t[:80000], re.S):
        paras.append(fn)
    # ltx_note 内联 address: 单位（IEEE 模板常见）
    for m_ in re.finditer(r'ltx_note_type">address:\s*</span>([^<]{4,120})', t[:80000]):
        paras.append(m_.group(1))
    insts, seen = [], set()
    for p_ in paras:
        segs = re.split(r"<sup[^>]*>[^<]*</sup>|(?=<b|\d\])", p_)
        # ltx_noindent 版本：整段是 "1]Inst A 2]Inst B"，按 \d] 切
        raw = re.sub(r"<[^>]+>", " ", p_)
        if re.search(r"\d\]", raw):
            segs = re.split(r"\s*\d+\]\s*", raw)
        # address: 前缀排版（部分模板）：单位跟在 "address:" 后
        if "address:" in raw.lower():
            m_ = re.search(r"address:\s*(.+)", raw, re.I | re.S)
            if m_:
                segs = [m_.group(1)] + list(segs)
        for seg in segs:
            txt = re.sub(r"<[^>]+>", "", seg)
            txt = re.sub(r"\s+", " ", txt).strip(" ,;·")
            if "@" in txt:
                continue
            if 3 < len(txt) < 130 and INST_HINT.search(txt):
                key = txt.lower()
                if key not in seen:
                    seen.add(key)
                    insts.append(txt)
        if len(insts) >= 2:
            break
    return insts[:2]


def load_cache():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:  # noqa: BLE001
            return {}
    return {}


def save_cache(cache):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)


def _fresh(rec):
    ts = rec.get("_ts", "")
    try:
        return (datetime.datetime.now() - datetime.datetime.fromisoformat(ts)).days < CACHE_TTL_DAYS
    except Exception:  # noqa: BLE001
        return False


def fetch_s2_citations(arxiv_id, tries=2):
    """Semantic Scholar 被引数（无 key，1rps 限流，带退避；全失败返回 None）。"""
    import urllib.error
    url = f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{arxiv_id}?fields=citationCount"
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "paper-daily/0.9"})
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.loads(r.read().decode("utf-8"))
                return d.get("citationCount")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(3 + 2 * i)
                continue
            return None
        except Exception:  # noqa: BLE001
            return None
    return None


def fetch_openalex(arxiv_id):
    """被引数 + 作者/高校。OpenAlex 对 arXiv 新论文收录有 1-3 天延迟，缺省时退 S2。"""
    try:
        d = http_json(
            f"https://api.openalex.org/works/doi:10.48550/arXiv.{arxiv_id}"
            "?select=cited_by_count,authorships"
        )
    except Exception:  # noqa: BLE001
        d = None
    if not d:
        # OpenAlex 未收录（太新）-> Semantic Scholar 拿被引
        c = fetch_s2_citations(arxiv_id)
        return {"cited_by": c} if c is not None else {}
    out_authors = []
    for a in d.get("authorships", [])[:12]:
        name = (a.get("author") or {}).get("display_name") or a.get("raw_author_name") or ""
        insts = []
        for aff in a.get("affiliations", []):
            for inst in aff.get("institutions", []):
                n = inst.get("display_name")
                if n and n not in insts:
                    insts.append(n)
        raw = a.get("raw_affiliation_strings") or []
        for r_ in raw:
            if r_ and r_ not in insts:
                insts.append(r_)
        out_authors.append({"name": name, "institutions": insts[:2]})
    return {"cited_by": d.get("cited_by_count", 0), "authors": out_authors}


def github_search_repo(title, stars_min=3):
    """按论文标题搜 GitHub 仓库（无 HF repo 时的兜底）。返回 (repo_url, stars) 或 (None, None)。
    只信 stars>=stars_min 且名称/描述与标题明显相关的第一结果，宁缺毋滥。"""
    import urllib.parse as _up
    q = _up.quote(title[:80])
    try:
        d = http_json(f"https://api.github.com/search/repositories?q={q}&per_page=5",
                      headers={"User-Agent": "paper-daily/0.9", "Accept": "application/vnd.github+json"})
    except Exception:  # noqa: BLE001
        return None, None
    items = d.get("items") or []
    if not items:
        return None, None
    tl = title.lower()
    key_words = [w for w in re.findall(r"[a-z]{4,}", tl) if w not in
                 ("with", "from", "towards", "using", "based", "rethinking", "efficient")]
    for it in items:
        name_desc = (it.get("full_name", "") + " " + (it.get("description") or "")).lower()
        # 标题前 3 个关键词中至少 2 个命中才认
        hit = sum(1 for w in key_words[:4] if w in name_desc)
        if hit >= 2 and it.get("stargazers_count", 0) >= stars_min:
            return it["html_url"], it["stargazers_count"]
    return None, None


def github_repo_stars(repo_url):
    """repo_url: https://github.com/owner/name -> stars:int|None（未鉴权，失败返回 None）"""
    m = re.match(r"https?://github\.com/([\w.-]+/[\w.-]+?)(?:\.git)?/?$", repo_url or "")
    if not m:
        return None
    try:
        d = http_json(f"https://api.github.com/repos/{m.group(1)}",
                      headers={"User-Agent": "paper-daily/0.9", "Accept": "application/vnd.github+json"})
        return d.get("stargazers_count")
    except Exception:  # noqa: BLE001
        return None


def enrich(papers, github_repos=None):
    """papers: [{arxiv_id, ...}]（仅精选后的少量论文）。就地写入 cited_by/authors/github/stars。"""
    cache = load_cache()
    github_repos = github_repos or {}
    for p in papers:
        aid = p["arxiv_id"]
        rec = cache.get(aid)
        if rec and _fresh(rec):
            for k in ("cited_by", "authors", "institutions", "github", "stars"):
                if rec.get(k) is not None:
                    p[k] = rec[k]
            continue
        rec = {"_ts": datetime.datetime.now().isoformat(timespec="seconds")}
        oa = fetch_openalex(aid)
        rec.update(oa)
        # 高校：OpenAlex 对 arXiv 预印本常无 raw_affiliation，优先 arXiv HTML 脚注
        insts = fetch_arxiv_affiliations(aid)
        if insts:
            rec["institutions"] = insts
        repo = github_repos.get(aid) or p.get("github") or ""
        stars = None
        if repo:
            stars = github_repo_stars(repo)
            time.sleep(0.4)  # 未鉴权限流保护
        else:
            # 兜底：按标题搜 GitHub（结果可信才写）
            repo, stars = github_search_repo(p.get("title") or "")
            time.sleep(0.4)
        rec["github"] = repo or None
        rec["stars"] = stars
        cache[aid] = rec
        for k in ("cited_by", "authors", "github", "stars"):
            if rec.get(k) is not None:
                p[k] = rec[k]
    save_cache(cache)
    return papers


if __name__ == "__main__":
    # 自测：python3 paper_meta.py 2608.26809
    if len(sys.argv) > 1:
        test = {"arxiv_id": sys.argv[1]}
        enrich([test], {"2608.26809": "https://github.com/Wucy0519/MMLVE"})
        print(json.dumps(test, ensure_ascii=False, indent=1)[:800])
