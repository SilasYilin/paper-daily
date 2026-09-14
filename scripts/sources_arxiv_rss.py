#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sources_arxiv_rss.py - arXiv RSS 通道（v1.3）

背景：本机出口 IP 对 arXiv API（/api/query）长期 429，导致候选池只剩 HF 的
几十篇。实测 RSS（rss.arxiv.org/rss/<cat>）不受影响，cs.CV 单日约 140+ 条，
且自带标题、摘要、作者、分类——足以作为 arXiv 主通道的替代。

输出 data/sources_arxiv_rss.json：
  {"generatedAt": "...", "items": {arxiv_id: {arxiv_id,title,abstract,authors,
                                              published,categories,comment}}}
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net  # noqa: E402

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(ROOT, "data")
OUT_PATH = os.path.join(DATA_DIR, "sources_arxiv_rss.json")

CATS = ["cs.CV", "cs.GR", "cs.AI", "cs.LG", "cs.RO", "cs.MM"]
NS = {
    "rss": "http://purl.org/rss/1.0/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "content": "http://purl.org/rss/1.0/modules/content/",
}


def _clean_abstract(desc: str) -> str:
    """RSS description 形如 '<p>arXiv:2609.1v1 Announce Type: new <br/>Abstract: ...</p>'"""
    txt = re.sub(r"<[^>]+>", " ", desc or "")
    txt = re.sub(r"&amp;", "&", txt)
    txt = re.sub(r"&lt;", "<", txt)
    txt = re.sub(r"&gt;", ">", txt)
    txt = re.sub(r"&#\d+;", " ", txt)
    txt = re.sub(r"arXiv:\S+\s*", " ", txt)
    txt = re.sub(r"Announce Type:\s*\w+", " ", txt, flags=re.I)
    # 去掉摘要尾部常见的 "Comments:" / "Subjects:" 元信息
    txt = re.split(r"\s*Comments:\s*|\s*Subjects:\s*|\s*Journal ref:\s*", txt)[0]
    idx = txt.find("Abstract:")
    if idx >= 0:
        txt = txt[idx + len("Abstract:"):]
    return re.sub(r"\s+", " ", txt).strip()


def _arxiv_id(link: str) -> str:
    m = re.search(r"abs/([0-9]{4}\.[0-9]{4,5})(v\d+)?", link or "")
    return m.group(1) if m else ""


def fetch_cat(cat: str, timeout: int = 45) -> list[dict]:
    url = f"https://rss.arxiv.org/rss/{cat}"
    txt = net.get_text(url, timeout=timeout, retries=2)
    try:
        root = ET.fromstring(txt)
    except ET.ParseError:
        return []
    out: list[dict] = []
    for item in root.iter("item"):
        link = (item.findtext("link") or "").strip()
        aid = _arxiv_id(link)
        if not aid:
            continue
        title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", item.findtext("title") or "")).strip()
        title = re.sub(r"^arXiv:\S+\s*", "", title)
        creators = [c.text.strip() for c in item.findall("dc:creator", NS) if c.text]
        if not creators:
            creators = [c.text.strip() for c in item.iter("{http://purl.org/dc/elements/1.1/}creator") if c.text]
        # RSS 常把全部作者塞进单条 creator（逗号分隔），拆开以便下游按 list 使用
        if len(creators) == 1 and "," in creators[0]:
            creators = [x.strip() for x in creators[0].split(",") if x.strip()]
        pub = (item.findtext("pubDate") or "").strip()
        cats = [c.text.strip() for c in item.findall("category") if c.text]
        out.append({
            "arxiv_id": aid,
            "title": title,
            "abstract": _clean_abstract(item.findtext("description") or ""),
            "authors": creators[:12],
            "published": _parse_pub(pub),
            "categories": cats,
            "comment": "",
            "_from_rss": True,
        })
    return out


def _parse_pub(pub: str) -> str:
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"):
        try:
            return datetime.datetime.strptime(pub, fmt).date().isoformat()
        except Exception:  # noqa: BLE001
            continue
    return datetime.date.today().isoformat()


def main(cats: list[str] | None = None) -> dict:
    cats = cats or CATS
    items: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(lambda c: (c, _safe(fetch_cat, c)), cats):
            cat, rows = res
            n0 = len(items)
            for r in rows:
                prev = items.get(r["arxiv_id"])
                if prev:
                    prev["categories"] = sorted(set(prev.get("categories") or []) | set(r.get("categories") or []))
                else:
                    items[r["arxiv_id"]] = r
            print(f"    [RSS] {cat}: {len(rows)} 条（新增 {len(items) - n0}）")
    payload = {
        "generatedAt": datetime.datetime.now().isoformat(timespec="seconds"),
        "cats": cats,
        "items": items,
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"    [RSS] 合计 {len(items)} 篇（去重后）")
    return payload


def _safe(fn, *a):
    try:
        return fn(*a)
    except Exception as e:  # noqa: BLE001
        print(f"    [RSS] {a[0] if a else ''} 失败：{type(e).__name__} {str(e)[:60]}", file=sys.stderr)
        return []


if __name__ == "__main__":
    cats = sys.argv[1:] or None
    main(cats)
