#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sources_wechat.py - 微信公众号检索源（基于 wechat-article-search skill 的搜狗通道）v1.0

变更（v1.0，2026-09-03）：
  - 替换原先依赖 opencli CDP 的 fetch_weixin：改用仓库内置 scripts/wechat_search/search_wechat.js
    （来自 wechat-article-search skill，搜狗微信搜索，无需登录、无浏览器依赖）。
  - 输出 schema 与旧 media_monitor.py 完全兼容（data/media_mentions.json），
    run_daily.py 的 media_signal() 无需改动；仅新增 account 字段（账号白名单加权用）。

用法：
  python scripts/sources_wechat.py            # 正常运行，写 data/media_mentions.json
  exit code 1 表示一条近期提及都没有（调用方可回退 media_monitor.py / opencli 通道）
"""
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(ROOT, "data")
SEARCH_JS = os.path.join(BASE_DIR, "wechat_search", "search_wechat.js")

def _ver_key(path: str):
    """从路径中解析语义化版本，用于挑选最新的受管 node（22.22.2-10 > 22.22.2-3）。"""
    m = re.search(r"(\d+)\.(\d+)\.(\d+)(?:-(\d+))?", path)
    if not m:
        return (0, 0, 0, 0)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4) or 0))


def _find_node():
    """node 可执行文件：环境变量 > 受管目录中最新版本 > PATH。

    注意：不要硬编码版本号——受管 node 升级（如 22.22.2-2 → -3）会让路径失效，
    而静默失败会被管道的「源失败自动降级」吞掉，表现为公众号源长期零结果。
    """
    env = os.environ.get("PAPER_DAILY_NODE")
    if env and os.path.exists(env):
        return env

    managed = r"C:\Users\25432\.workbuddy\binaries\node\versions"
    if os.path.isdir(managed):
        cands = sorted(
            (os.path.join(managed, d, "node.exe") for d in os.listdir(managed)),
            key=_ver_key,
        )
        for p in reversed([c for c in cands if os.path.exists(c)]):
            try:
                if subprocess.run([p, "--version"], capture_output=True, timeout=15).returncode == 0:
                    return p
            except Exception:  # noqa: BLE001
                continue

    try:
        if subprocess.run(["node", "--version"], capture_output=True, timeout=15).returncode == 0:
            return "node"
    except Exception:  # noqa: BLE001
        pass
    return "node"


NODE = _find_node()

# v1（2026-09-14）：用户指令「去掉检索源限制」——不再限定公众号、不再限定定向组合词，
# 改为按研究方向做宽检索；点名公众号仅作为加权参考，不再作为过滤条件。
WX_ACCOUNTS = ["机器之心", "量子位", "我爱计算机视觉", "3D视觉工坊", "新视学院"]
QUERIES_WX = [
    "稀疏视角 三维重建", "4D高斯 新视角合成", "高斯泼溅 动态场景",
    "新视角合成 论文", "三维重建 前馈", "VGGT 三维", "DUSt3R 重建",
    "世界模型 视频生成", "深度估计 位姿", "单目视频 4D重建",
    "三维重建 最新", "视频扩散 三维",
]
RECENT_DAYS = 30          # 每日更新的媒体信号只要最近 30 天（原 120 天窗口太宽，旧文噪声大）
PER_QUERY = 8            # 每个查询取前 8 条
ARXIV_RE = re.compile(r"\b(\d{4}\.\d{4,5})\b")


def search_once(query: str, n: int) -> list:
    """调一次 node 脚本，返回 articles 列表（失败返回 []）。"""
    fd, out_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        r = subprocess.run(
            [NODE, SEARCH_JS, query, "-n", str(n), "-o", out_path],
            capture_output=True, text=True, timeout=90,
            cwd=os.path.dirname(SEARCH_JS),
        )
        if r.returncode != 0 or not os.path.exists(out_path):
            return []
        with open(out_path, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("articles") or []
    except Exception:  # noqa: BLE001
        return []
    finally:
        try:
            os.remove(out_path)
        except OSError:
            pass


def parse_dt(s: str):
    s = (s or "").strip()
    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    result = {"fetched_at": datetime.datetime.now().isoformat(timespec="seconds"),
              "channel": "wechat-article-search(skill)/sogou", "mentions": []}
    seen = set()
    cutoff = datetime.date.today() - datetime.timedelta(days=RECENT_DAYS)
    total_fetched = 0

    for q in QUERIES_WX:
        arts = search_once(q, PER_QUERY)
        total_fetched += len(arts)
        for it in arts:
            title = (it.get("title") or "").strip()
            key = title[:40]
            if not title or key in seen:
                continue
            d = parse_dt(it.get("datetime") or it.get("date_text") or "")
            if d is None or d < cutoff:      # 时间窗过滤（旧教程/旧文剔除）
                continue
            seen.add(key)
            text = title + " " + (it.get("summary") or "")
            m = ARXIV_RE.search(text)
            result["mentions"].append({
                "source": "weixin",
                "query": q,
                "title": title,
                "summary": (it.get("summary") or "")[:200],
                "time": (it.get("datetime") or "")[:10],
                "arxiv_id": m.group(1) if m else None,
                "url": it.get("url") or "",
                "account": it.get("source") or "",
            })

    mentions = result["mentions"]
    path = os.path.join(DATA_DIR, "media_mentions.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)

    in_accounts = sum(1 for m_ in mentions if m_.get("account") in WX_ACCOUNTS)
    print(f"[sources_wechat] {len(QUERIES_WX)} 个查询共抓到 {total_fetched} 条，"
          f"近 {RECENT_DAYS} 天窗口内 {len(mentions)} 条（点名账号 {in_accounts} 条）-> {path}")

    if not mentions:
        sys.exit(1)   # 一条都没有 -> 让调用方回退 opencli 通道


if __name__ == "__main__":
    main()
