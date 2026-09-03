#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sources_extra.py - 扩展信息源（v0.4）

按用户 2026-08-28 22:49 需求扩充：
  1. HF Daily Papers（hf-mirror.com 直连）-- upvote ≥30 作为热度轨信号，upvote 写入 influence
  2. 论文时间窗放宽：最近 N 天（默认 120 天）都算「最新」，当天无合适论文可显示无
  3. 排除偏门方向：医学影像/纯机器人/超声/病理等（exclude_keywords）

输出：data/sources_extra.json（run_daily.py 合并使用）
"""
import datetime
import json
import os
import re
import sys
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(ROOT, "data")

HF_MIRROR = "https://hf-mirror.com/api/daily_papers"
HF_DAYS = 7           # 拉最近 7 天的 daily papers（每天 50 篇，共约 350 条去重后~200）
HF_MIN_UPVOTES = 30   # 双轨制约定：upvote >= 30 作为热度信号

# 偏门方向排除（用户点名：医学、纯机器人；另加病理/超声/眼科/自动驾驶纯应用等）
EXCLUDE_KEYWORDS = [
    "medical", "clinical", "patient", "hospital", "radiology", "patholog",
    "ultrasound", "fetal", "tumor", "cancer", "lesion", "endoscop",
    "surgical", "diagnos", "disease", "ecg", "eeg signal", "ct scan", "mri ",
    "robot", "manipulat", "embodied manipulation", "grasping", "locomotion",
    "autonomous driving", "self-driving", "lidar", "point cloud seg for driving",
    "fingerprint", "face recognition", "remote sensing", "satellite", "agricultur",
    "wireless", "network", "circuit", "hardware design", "fpga",
]


_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def http_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "paper-daily/0.4"})
    with _OPENER.open(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_hf_daily(days=HF_DAYS):
    """拉最近 N 天 HF daily papers，返回 {arxiv_id: {upvotes, publishedAt, title}}"""
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
            arxiv_id = m.group(1)
            up = int(paper.get("upvotes") or 0)
            if arxiv_id not in seen or up > seen[arxiv_id]["upvotes"]:
                seen[arxiv_id] = {
                    "upvotes": up,
                    "publishedAt": (paper.get("publishedAt") or "")[:10],
                    "title": paper.get("title") or "",
                }
    return seen


def is_excluded(title: str, abstract: str = "") -> bool:
    text = (title + " " + abstract).lower()
    return any(k in text for k in EXCLUDE_KEYWORDS)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"[sources_extra] 拉取 HF daily papers 最近 {HF_DAYS} 天 ...")
    hf = fetch_hf_daily()
    hot = {k: v for k, v in hf.items() if v["upvotes"] >= HF_MIN_UPVOTES}
    print(f"[sources_extra] HF 去重后 {len(hf)} 篇，其中 upvote>={HF_MIN_UPVOTES} 热门 {len(hot)} 篇")

    out = {
        "fetched_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "hf_daily": hf,
        "hf_hot": hot,
        "exclude_keywords": EXCLUDE_KEYWORDS,
    }
    path = os.path.join(DATA_DIR, "sources_extra.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"[sources_extra] 写出 {path}")


if __name__ == "__main__":
    main()
