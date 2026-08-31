#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
media_monitor.py - 中文媒体源监控（公众号/B站/小红书）v0.1

实测可用性（2026-08-28 沙箱）：
  ✅ 公众号（搜狗微信搜索，标题+摘要+时间，无需登录）
  ✅ B站（opencli bilibili search，无需登录）
  ⛔ 小红书/知乎/X/抖音：登录墙（AUTH_REQUIRED），需人工登录后才能接

用途：找到「最近几个月」中文社区在讨论的论文线索（标题关键词 -> arXiv ID 匹配），
     作为热度轨补充信号 + 中文社区线索卡。输出 data/media_mentions.json
"""
import datetime
import json
import os
import re
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(ROOT, "data")
ENV = dict(os.environ, OPENCLI_CDP_ENDPOINT="http://127.0.0.1:9222")

# 查询词（偏好方向 + 用户本地论文库检索词校准 2026-08-29；含点名公众号账号）
# v0.9（用户 2026-08-31 审查指令）：只查用户点名的 5 个公众号；B站移除
WX_ACCOUNTS = ["机器之心", "量子位", "我爱计算机视觉", "3D视觉工坊", "新视学院"]
QUERIES_WX = ["机器之心 三维重建", "量子位 世界模型", "机器之心 世界模型", "量子位 三维重建",
              "我爱计算机视觉 3D", "3D视觉工坊 三维", "新视学院 论文",
              "3D视觉工坊 世界模型", "我爱计算机视觉 高斯", "新视学院 3DGS"]
QUERIES_BILI = []  # v0.9：B站源移除（用户指令）
RECENT_DAYS = 120
# arXiv ID 匹配（2608.19583 风格）
ARXIV_RE = re.compile(r"\b(\d{4}\.\d{4,5})\b")


def sh(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=ENV)
        if r.returncode != 0:
            return None, (r.stdout or "") + (r.stderr or "")
        return r.stdout, None
    except subprocess.TimeoutExpired:
        return None, "timeout"


def fetch_weixin(query):
    out, err = sh(["opencli", "weixin", "search", query, "--limit", "10", "-f", "json"])
    if not out:
        return []
    items = []
    for chunk in re.findall(r"\[.*?\](?=\s*\[|\s*$)", out, re.S):
        try:
            items += json.loads(chunk)
        except json.JSONDecodeError:
            continue
    return items


def fetch_bilibili(query):
    out, err = sh(["opencli", "bilibili", "search", query, "--limit", "10", "-f", "json"])
    if not out:
        return []
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        try:
            m = re.search(r"\[.*\]", out, re.S)
            return json.loads(m.group(0)) if m else []
        except Exception:  # noqa: BLE001
            return []


def within_window(item, days=RECENT_DAYS):
    pt = str(item.get("publish_time") or item.get("pubdate") or item.get("time") or "")
    # 相对时间（X小时前/X天前/昨天/今天）一律算近期
    if any(k in pt for k in ["小时前", "分钟前", "天前", "昨天", "今天", "周前"]) and "月" not in pt:
        return True
    m = re.match(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", pt)
    if not m:
        return False
    try:
        d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return False
    return d >= datetime.date.today() - datetime.timedelta(days=days)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    result = {"fetched_at": datetime.datetime.now().isoformat(timespec="seconds"), "mentions": []}
    seen = set()

    for q in QUERIES_WX:
        for it in fetch_weixin(q):
            key = (it.get("title") or "")[:40]
            if not key or key in seen:
                continue
            seen.add(key)
            aid = None
            m = ARXIV_RE.search((it.get("title") or "") + " " + (it.get("summary") or ""))
            if m:
                aid = m.group(1)
            result["mentions"].append({
                "source": "weixin", "query": q,
                "title": it.get("title") or "",
                "summary": (it.get("summary") or "")[:200],
                "time": it.get("publish_time") or "",
                "arxiv_id": aid,
                "url": it.get("url") or "",
            })

    for q in QUERIES_BILI:
        for it in fetch_bilibili(q):
            key = (it.get("title") or "")[:40]
            if not key or key in seen:
                continue
            seen.add(key)
            aid = None
            m = ARXIV_RE.search((it.get("title") or "") + " " + str(it.get("desc") or ""))
            if m:
                aid = m.group(1)
            result["mentions"].append({
                "source": "bilibili", "query": q,
                "title": it.get("title") or "",
                "summary": str(it.get("desc") or "")[:200],
                "time": it.get("pubdate") or "",
                "arxiv_id": aid,
                "url": it.get("url") or "",
            })

    # 只保留时间窗内的（B 站无日期字段：标题/摘要含 2025/2026/RSS/CVPR 等近期会议标记即保留）
    def bili_recent(m):
        text = (m["title"] + " " + m["summary"]).lower()
        return any(k in text for k in ["2026", "2025", "cvpr", "iccv", "eccv", "neurips", "rss", "icra", "iclr", "icml"])
    fresh = [m for m in result["mentions"] if m["source"] == "bilibili" or within_window(m)]
    fresh = [m for m in fresh if m["source"] == "weixin" or bili_recent(m)]
    result["mentions"] = fresh
    path = os.path.join(DATA_DIR, "media_mentions.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(f"[media_monitor] 抓到 {len(fresh)} 条媒体提及（公众号+B站）-> {path}")


if __name__ == "__main__":
    main()
