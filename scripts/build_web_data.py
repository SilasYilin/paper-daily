#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_web_data.py - today.json -> web/data.js（契约兼容版）
按 HANDOFF-run_daily.md 第六节：hero = score 最高；summary 回退 summary_one_liner；
figure.url 由 figure_url 映射，null 时网页不渲染图；输出 window.PAPER_DAILY_DATA。
（用户本地已有正式版同名脚本，此版为服务器侧契约兼容实现，接口一致可互换。）
"""
import argparse
import datetime
import json
import os

FIELDS = ("background", "task", "insight", "pipeline", "methods", "experiment", "limitation")


def normalize(p: dict) -> dict:
    summary = p.get("summary") or p.get("summary_one_liner") or ""
    fig = p.get("figure_url") or None
    return {
        "title": p.get("title", ""),
        "titleZh": p.get("title_zh", "") or "",
        "hook": p.get("hook", "") or "",
        "cards": p.get("cards", []) or [],
        "figureNote": p.get("figure_note", "") or "",
        "figures": p.get("figures", []) or [],
        "authors": p.get("authors", ""),
        "venue": p.get("venue", ""),
        "summary": summary,
        "paperUrl": p.get("paper_url", ""),
        "score": p.get("score", 0),
        "scores": p.get("scores", {}) or {},
        "category": p.get("category", ""),
        "influence": p.get("influence", ""),
        "github": p.get("github", "") or "",
        "stars": p.get("stars"),
        "citedBy": p.get("cited_by"),
        "institutions": p.get("institutions", []) or [],
        "figure": {"url": fig, "caption": p.get("figure_caption", "")},
        "fields": {k: (p.get("fields") or {}).get(k, "") for k in FIELDS},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--issue", default="")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--axes", default="三维重建 × 世界模型")
    ap.add_argument("--ed-note", default="本期精选基于偏好画像筛选与排序。")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        papers = json.load(f)
    normalized = [normalize(p) for p in papers]
    normalized.sort(key=lambda x: x["score"], reverse=True)
    hero = normalized[0] if normalized else None
    rest = normalized[1:]

    data = {
        "issue": args.issue,
        "date": args.date,
        "axes": args.axes,
        "edNote": args.ed_note,
        "hero": hero,
        "papers": rest,
        "counts": {"total": len(normalized), "new": len(rest)},
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("window.PAPER_DAILY_DATA = ")
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write(";\n")
    print(f"[build_web_data] {args.input} -> {args.output}（hero: {hero['title'][:40] if hero else '无'}，其余 {len(rest)} 篇）")


if __name__ == "__main__":
    main()
