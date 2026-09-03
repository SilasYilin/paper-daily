#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sources_hf.py - Hugging Face Daily Papers 主源（v0.9，第一优先级）

用户 2026-08-31 指令：HF daily papers 为第一优先级论文来源（社区筛选过的高质量流），
arXiv 降为兜底。抓最近 N 天 daily papers 全量，直接作为候选池：
  - 自带 githubRepo（封面 star 链接的权威来源）
  - upvotes 作为社区热度信号
输出：data/sources_hf.json {arxiv_id: {..., upvotes, githubRepo, publishedAt}}
"""
import datetime
import json
import os
import re
import sys
import urllib.request

# 直连 opener（绕过可能失效的本地 http_proxy 环境变量）
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(ROOT, "data")

HF_MIRROR = "https://hf-mirror.com/api/daily_papers"
HF_DAYS = 7  # 最近 7 天（每天 50 篇，去重约 300 条，社区每日精选）


def http_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "paper-daily/0.9"})
    with _OPENER.open(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_hf_daily(days=HF_DAYS):
    seen = {}
    today = datetime.date.today()
    for back in range(days):
        day = (today - datetime.timedelta(days=back)).isoformat()
        try:
            items = http_json(f"{HF_MIRROR}?day={day}")
        except Exception as e:  # noqa: BLE001
            print(f"    [HF] {day} 拉取失败（{e}），跳过", file=sys.stderr)
            continue
        for p in items:
            paper = p.get("paper") or {}
            aid = paper.get("id") or ""
            m = re.search(r"(\d{4}\.\d{4,5})", aid)
            if not m:
                continue
            aid = m.group(1)
            rec = seen.get(aid)
            up = p.get("upvotes") or paper.get("upvotes") or 0
            if rec is None:
                seen[aid] = {
                    "arxiv_id": aid,
                    "title": paper.get("title") or "",
                    "upvotes": up,
                    "githubRepo": paper.get("githubRepo") or "",
                    "publishedAt": paper.get("publishedAt") or "",
                }
            else:  # 同篇多日出现取最高 upvote（今日热度回落则保留峰值）
                rec["upvotes"] = max(rec["upvotes"], up)
    return seen


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    data = fetch_hf_daily()
    out = {"hf_daily": data, "fetched_at": datetime.datetime.now().isoformat(timespec="seconds")}
    with open(os.path.join(DATA_DIR, "sources_hf.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    hot = sum(1 for v in data.values() if v["upvotes"] >= 30)
    print(f"[HF] {len(data)} 篇（7 天去重），热门(>=30) {hot} 篇 -> data/sources_hf.json")


if __name__ == "__main__":
    main()
