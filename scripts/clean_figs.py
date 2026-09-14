#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_figs.py - 清理 web/figs 中已不再被引用的历史配图

背景：每期约 8 张图（压缩后合计 ~1MB），若不清理，仓库体积会线性增长。
策略：解析 web/data.js，保留 hero + papers 的 figures[].file 所引用的文件；
      其余文件放入回收目录 web/figs_trash/<YYYYMMDD>/ 而非直接删除，便于回滚。

用法：
    python scripts/clean_figs.py            # 试运行（只报告，不移动）
    python scripts/clean_figs.py --apply    # 实际移入回收目录
    python scripts/clean_figs.py --purge    # 连回收目录一起删除（谨慎）
"""
import argparse
import datetime
import json
import os
import re
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
WEB = os.path.join(ROOT, "web")
FIGS = os.path.join(WEB, "figs")
TRASH = os.path.join(WEB, "figs_trash")


def referenced_files() -> set[str]:
    """从 web/data.js 解析出当前被引用的图片文件名。"""
    p = os.path.join(WEB, "data.js")
    if not os.path.exists(p):
        raise SystemExit(f"[clean_figs] 未找到 {p}")
    raw = open(p, encoding="utf-8").read()
    payload = raw[raw.index("{"): raw.rindex("}") + 1]
    data = json.loads(payload)
    names = set()
    for item in [data.get("hero")] + (data.get("papers") or []):
        if not item:
            continue
        for f in item.get("figures") or []:
            if f.get("file"):
                names.add(os.path.basename(f["file"]))
    return names


def human(n: int) -> str:
    return f"{n/1024:.0f}KB" if n < 1024 * 1024 else f"{n/1048576:.1f}MB"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="实际移入回收目录")
    ap.add_argument("--purge", action="store_true", help="删除回收目录（需先 --apply 过）")
    args = ap.parse_args()

    if args.purge:
        if os.path.isdir(TRASH):
            shutil.rmtree(TRASH)
            print(f"[clean_figs] 已删除回收目录 {TRASH}")
        else:
            print("[clean_figs] 回收目录不存在，跳过")
        return

    if not os.path.isdir(FIGS):
        print("[clean_figs] figs 目录不存在，跳过")
        return

    keep = referenced_files()
    stale, total = [], 0
    for fn in sorted(os.listdir(FIGS)):
        fp = os.path.join(FIGS, fn)
        if not os.path.isfile(fp) or fn in keep:
            continue
        if not re.search(r"\.(png|jpe?g|webp|gif|svg)$", fn, re.I):
            continue
        stale.append((fn, os.path.getsize(fp)))
        total += os.path.getsize(fp)

    print(f"[clean_figs] 本期引用 {len(keep)} 张；历史残留 {len(stale)} 张，合计 {human(total)}")
    for fn, sz in stale:
        print(f"    - {fn} ({human(sz)})")
    if not stale:
        print("[clean_figs] 无需清理")
        return
    if not args.apply:
        print("[clean_figs] 试运行：加 --apply 才会移动")
        return

    day = datetime.date.today().strftime("%Y%m%d")
    dest = os.path.join(TRASH, day)
    os.makedirs(dest, exist_ok=True)
    for fn, _ in stale:
        shutil.move(os.path.join(FIGS, fn), os.path.join(dest, fn))
    print(f"[clean_figs] 已移入 {dest}（回滚：复制回 web/figs/ 即可）")


if __name__ == "__main__":
    main()
