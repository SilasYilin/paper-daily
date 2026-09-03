#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_llm.py - 把智能体（WorkBuddy 会话）撰写的精读总结合并进 data/today.json

用法：
  1) 会话/自动化智能体按 LLM_JSON 契约撰写总结，写入 data/llm_summaries.json：
     { "<arxiv_id>": { "title_zh","hook","summary","cards","figure_note","category",
                       "scores","influence","fields" }, ... }
     （即 run_daily.py 中 LLM_JSON_INSTRUCTION 的输出对象，按 arXiv ID 索引）
  2) python scripts/merge_llm.py   # 合并进 data/today.json（只覆盖上述键，其余保留）

红线：不存在的键不新增、缺失的论文跳过并警告；绝不编造数值。
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(ROOT, "data")

LLM_KEYS = ("title_zh", "hook", "summary", "cards", "figure_note", "category", "scores", "influence", "fields")


def main():
    today_path = os.path.join(DATA_DIR, "today.json")
    llm_path = os.path.join(DATA_DIR, "llm_summaries.json")
    with open(today_path, encoding="utf-8") as f:
        today = json.load(f)
    with open(llm_path, encoding="utf-8") as f:
        llm = json.load(f)

    merged = 0
    for p in today:
        aid = (p.get("paper_url") or "").rsplit("/", 1)[-1]
        patch = llm.get(aid)
        if not patch:
            print(f"[merge_llm] 跳过 {aid}（无总结）")
            continue
        for k in LLM_KEYS:
            if patch.get(k) is not None:
                p[k] = patch[k]
        # 合并成功则去掉兜底痕迹
        sc = p.get("scores") or {}
        if isinstance(sc, dict):
            sc.pop("note", None)
        merged += 1
        print(f"[merge_llm] {aid} <- {patch.get('title_zh', '')[:30]}")

    with open(today_path, "w", encoding="utf-8") as f:
        json.dump(today, f, ensure_ascii=False, indent=2)
    print(f"[merge_llm] 完成：{merged}/{len(today)} 篇已替换为智能体精读总结")


if __name__ == "__main__":
    main()
