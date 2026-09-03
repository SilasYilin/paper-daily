#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sources_aihot.py - AI HOT 中文策展池检索源 v1.0

数据源：AI HOT v1 匿名只读 API（https://aihot.virxact.com），遵循 aihot skill 契约：
  1) 精选论文池：GET /api/v1/items?mode=selected&window=7d&category=paper&limit=50
  2) 关键词查询：先查精选池（mode=selected），为空则用同参数回查全量池（mode=all）
     并标注 selected=false（「未进入精选」）。
  3) cursor 不跨查询复用；本脚本每查询只取第一页（limit 内），不做翻页。

输出：data/sources_aihot.json
  {
    "fetched_at": ...,
    "curated": [ {arxiv_id, title, originalTitle, summary, source, url, publishedAt, score} ],
    "kw_hits": [ {query, mode, count, items: [...] } ],
    "signals": { "<arxiv_id>": {"weight": 0.08|0.06|0.02, "where": "...", "title": "..."} }
  }
  signals 供 run_daily.py 合并加权：精选论文池命中 +0.08；关键词精选池命中 +0.06；
  关键词全量池（未进精选）命中 +0.02。同一论文取最高权重，多来源叠加封顶 +0.10。
"""
import datetime
import json
import os
import re
import time
import urllib.parse
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(ROOT, "data")

API = "https://aihot.virxact.com/api/v1/items"
UA = "paper-daily/1.0 (+https://github.com/SilasYilin/paper-daily; aihot-skill compatible)"
ARXIV_URL_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", re.I)
ARXIV_TEXT_RE = re.compile(r"\b(\d{4}\.\d{4,5})\b")

# 偏好六轴对应的检索词（中英混合，服务端 q 搜索）
KW_QUERIES = [
    "三维重建", "世界模型", "3D reconstruction", "world model",
    "Gaussian Splatting", "NeRF", "4D", "spatial intelligence",
    "3D vision", "scene understanding",
]

W_CURATED = 0.08   # 精选论文池命中
W_KW_SEL = 0.06    # 关键词·精选池命中
W_KW_ALL = 0.02    # 关键词·全量池（未进入精选）命中
W_CAP = 0.10       # 单篇叠加封顶


# 强制直连（沙箱/本机的 http_proxy 指向不存在的本地代理时，urllib 会连接被拒）
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def http_json(url: str, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with _OPENER.open(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def build_url(**params) -> str:
    clean = {k: v for k, v in params.items() if v is not None}
    return f"{API}?{urllib.parse.urlencode(clean)}"


def slim(item: dict) -> dict:
    links = item.get("links") or {}
    text_all = " ".join(filter(None, [item.get("title") or "", item.get("originalTitle") or ""]))
    aid = None
    for url in (links.get("original"), links.get("aihot")):
        if url:
            m = ARXIV_URL_RE.search(url)
            if m:
                aid = m.group(1)
                break
    if not aid:
        m = ARXIV_TEXT_RE.search(text_all)
        if m:
            aid = m.group(1)
    return {
        "id": item.get("id"),
        "arxiv_id": aid,
        "title": item.get("title") or "",
        "originalTitle": item.get("originalTitle") or "",
        "summary": (item.get("summary") or "")[:300],
        "source": (item.get("source") or {}).get("name") or "",
        "url": links.get("original") or links.get("aihot") or "",
        "aihotUrl": links.get("aihot") or "",
        "publishedAt": item.get("publishedAt"),
        "discoveredAt": item.get("discoveredAt"),
        "score": item.get("score"),
        "selected": item.get("selected"),
    }


def fetch_page(params: dict) -> list:
    try:
        out = http_json(build_url(**params))
        return out.get("items") or []
    except Exception as e:  # noqa: BLE001
        print(f"    [aihot] 请求失败 {params}: {e}", flush=True)
        return []


def add_signal(signals: dict, aid: str, weight: float, where: str, title: str):
    if not aid:
        return
    cur = signals.get(aid)
    if not cur or weight > cur["weight"]:
        signals[aid] = {"weight": weight, "where": where, "title": title}
    else:
        # 多来源叠加，封顶
        merged = min(cur["weight"] + weight, W_CAP)
        cur["weight"] = merged
        cur["where"] += f";{where}"


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    signals: dict = {}
    curated_raw, kw_hits = [], []

    # 1) 精选论文池（category=paper）
    items = fetch_page({"mode": "selected", "window": "7d", "category": "paper", "limit": 50})
    curated = [slim(x) for x in items]
    curated_raw = curated
    for c in curated:
        add_signal(signals, c["arxiv_id"], W_CURATED, "curated-paper", c["title"])
    print(f"[sources_aihot] 精选论文池 7d: {len(curated)} 条", flush=True)
    time.sleep(0.6)

    # 2) 关键词查询：精选池优先，空则回查全量池并标注「未进入精选」
    for q in KW_QUERIES:
        items = fetch_page({"mode": "selected", "window": "7d", "q": q, "limit": 20})
        mode = "selected"
        if not items:
            time.sleep(0.4)
            items = fetch_page({"mode": "all", "window": "7d", "q": q, "limit": 20})
            mode = "all"
        slimmed = [slim(x) for x in items]
        kw_hits.append({"query": q, "mode": mode, "count": len(slimmed), "items": slimmed[:12]})
        w = W_KW_SEL if mode == "selected" else W_KW_ALL
        for c in slimmed:
            add_signal(signals, c["arxiv_id"], w, f"kw:{q}({mode})", c["title"])
        print(f"[sources_aihot] 关键词「{q}」: {len(slimmed)} 条（{mode}）", flush=True)
        time.sleep(0.5)

    out = {
        "fetched_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "api": API,
        "curated": curated_raw,
        "kw_hits": kw_hits,
        "signals": signals,
    }
    path = os.path.join(DATA_DIR, "sources_aihot.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"[sources_aihot] 信号覆盖 {len(signals)} 个 arXiv ID -> {path}", flush=True)


if __name__ == "__main__":
    main()
