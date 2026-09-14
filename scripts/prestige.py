#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prestige.py - 来源声望评分（v1.3）

用户 2026-09-14 指令：优先检索「知名大学 / 企业发表的论文」或「CCF-A 类会议的
Highlight、Oral 等优秀论文」，同时贴合「稀疏视角 4DGS × 新视角合成」主线。

本模块只负责回答两个问题：
  1. 这篇论文是不是顶会/顶刊论文？有没有 Oral / Highlight / Best Paper 等荣誉？
  2. 作者单位是不是顶级高校或知名企业研究院？

输入来自 arxiv_web.py 抓到的 comment（arXiv 的 Comments 字段常写
"CVPR 2026 Highlight" / "Accepted to ICCV 2025 (Oral)"）与作者机构脚注。
"""
from __future__ import annotations

import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
CONFIG_PATH = os.path.join(ROOT, "config", "source-prestige.json")

_cache: dict | None = None


def load_config() -> dict:
    global _cache
    if _cache is None:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            _cache = json.load(f)
    return _cache


def _rx(pattern: str) -> re.Pattern:
    """短全大写缩写用大小写敏感匹配，避免 MIT 命中 submit、HIT 命中 hit。"""
    flags = 0 if (pattern.isupper() and len(pattern) <= 6) else re.I
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(pattern) + r"(?![A-Za-z0-9])", flags)


def _build(pats: list[str]) -> list[tuple[str, re.Pattern]]:
    return [(p, _rx(p)) for p in pats]


class Prestige:
    def __init__(self, cfg: dict | None = None):
        cfg = cfg or load_config()
        self.cfg = cfg
        self.sc = cfg.get("scoring", {})
        v = cfg.get("venues", {})
        self.v1 = _build(v.get("tier1", []))
        self.v2 = _build(v.get("tier2", []))
        a = cfg.get("awards", {})
        self.aw_best = _build(a.get("best", []))
        self.aw_oral = _build(a.get("oral", []))
        i = cfg.get("institutions", {})
        self.i_top = _build(i.get("top", []))
        self.i_good = _build(i.get("good", []))

    # ---------- 会议 / 荣誉 ----------
    def venue(self, text: str) -> tuple[float, str, str]:
        """返回 (bonus, venue_name, award_label)。text 为 arXiv Comments + Journal-ref。"""
        text = text or ""
        if not text.strip():
            return 0.0, "", ""
        bonus, venue = 0.0, ""
        for name, rx in self.v1:
            if rx.search(text):
                bonus = self.sc.get("venue_tier1", 0.20)
                venue = name
                break
        if not venue:
            for name, rx in self.v2:
                if rx.search(text):
                    bonus = self.sc.get("venue_tier2", 0.10)
                    venue = name
                    break
        award = ""
        for name, rx in self.aw_best:
            if rx.search(text):
                award = "Best Paper" if "best" in name.lower() else name
                bonus += self.sc.get("award_best", 0.22)
                break
        else:
            for name, rx in self.aw_oral:
                if rx.search(text):
                    award = "Oral/Highlight" if name.lower() in ("oral", "highlight") else name
                    bonus += self.sc.get("award_oral", 0.14)
                    break
        # Workshop 论文 ≠ 主会论文：明确标注并整体降档，避免把 workshop 当作 CCF-A 正会
        if venue and re.search(r"\bworkshop\b", text, re.I):
            venue = f"{venue} Workshop"
            bonus *= 0.5
        return bonus, venue, award

    # ---------- 机构 ----------
    def institution(self, affiliations: list[str] | str) -> tuple[float, str]:
        text = affiliations if isinstance(affiliations, str) else " | ".join(affiliations or [])
        if not text.strip():
            return 0.0, ""
        for name, rx in self.i_top:
            if rx.search(text):
                return self.sc.get("inst_top", 0.16), name
        # 次级档：只给小幅加成（"知名机构优先"由 top 档体现），
        # 标签取原文命中的那一段，比 "University" 这类泛词更有信息量
        for name, rx in self.i_good:
            if rx.search(text):
                seg = text
                for part in re.split(r"[|/·,;]", text):
                    if rx.search(part):
                        seg = part.strip()
                        break
                return self.sc.get("inst_good", 0.04), seg[:40]
        return 0.0, ""

    # ---------- 汇总 ----------
    def evaluate(self, comment: str = "", journal_ref: str = "",
                 affiliations: list[str] | str | None = None, title: str = "") -> dict:
        vb, venue, award = self.venue(" ".join(x for x in (comment, journal_ref) if x))
        ib, inst = self.institution(affiliations or [])
        # 标题里出现会议名的情况（部分论文标题写作 "XXX: A CVPR 2026 Paper"）极少，只作弱信号
        if not venue and title:
            vb2, venue2, _ = self.venue(title)
            if venue2:
                vb, venue = vb2 * 0.6, venue2
        cap = self.sc.get("cap", 0.42)
        total = min(cap, vb + ib)
        labels: list[str] = []
        if venue:
            labels.append(venue)
        if award:
            labels.append(award)
        if inst:
            labels.append(inst)
        return {
            "bonus": round(total, 3),
            "venue": venue,
            "award": award,
            "institution": inst,
            "labels": labels,
        }


_DEFAULT: Prestige | None = None


def default() -> Prestige:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = Prestige()
    return _DEFAULT


if __name__ == "__main__":
    p = default()
    samples = [
        ("CVPR 2026 Highlight. Project page: ...", "", ["Tsinghua University", "Shanghai AI Laboratory"]),
        ("Accepted to ICCV 2025 (Oral)", "", ["Google DeepMind"]),
        ("", "IEEE TPAMI 2026", ["Some Unknown College"]),
        ("Best Paper Award at ECCV 2024", "", []),
        ("12 pages, 5 figures", "", ["A Small Lab"]),
    ]
    for c, j, a in samples:
        r = p.evaluate(comment=c, journal_ref=j, affiliations=a)
        print(f"{str(a):52s} | {c[:40]:42s} -> +{r['bonus']:.2f} {r['labels']}")
