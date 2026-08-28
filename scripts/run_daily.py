#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_daily.py — 每日论文检索管道主脚本 v0.2
按 HANDOFF-run_daily.md（2026-08-28）契约实现：
  arXiv API 抓取 -> 偏好画像打分硬过滤 -> LLM 总结（可选，DeepSeek）-> data/today.json(list)
  -> 串联 build_web_data.py 产出 web/data.js

用法:
  python3 scripts/run_daily.py                       # 全流程（抓取+写today.json+生成web/data.js）
  python3 scripts/run_daily.py --dry-run             # 只产出 data/today.json，不调用 build、不覆盖线上 data.js
  python3 scripts/run_daily.py --categories cs.CV    # 自定义分类（默认 cs.CV,cs.AI,cs.LG,cs.RO）
  python3 scripts/run_daily.py --max 6               # 精选篇数（默认 8，契约范围 5~8）

红线（契约第九节）：
  - 不编造数字：LLM 兜底/失败时一切数值写「以原文为准」
  - figure_url 一律 null（用户偏好简洁无图）
  - arXiv 抓取失败 -> 保留上期 data.js 不覆盖，退出码非 0
  - feedback_log 只读取，绝不写入/清空
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
PROFILE_PATH = os.path.join(ROOT, "config", "preference-profile.json")
DATA_DIR = os.path.join(ROOT, "data")
TODAY_JSON = os.path.join(DATA_DIR, "today.json")
BUILD_SCRIPT = os.path.join(BASE_DIR, "build_web_data.py")

ARXIV_API = "https://export.arxiv.org/api/query"  # HTTP 会 301 到 HTTPS，直接走 HTTPS
AXES_TITLE = "三维重建 × 世界模型"

ATOM_NS = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}


# ---------------------------------------------------------------- arXiv 抓取
def http_get(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "paper-daily/0.2 (research digest; contact: none)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_arxiv(categories, max_results: int = 150, retries: int = 1):
    """抓取 arXiv Atom API，返回 entry 列表；失败抛 RuntimeError。"""
    query = " OR ".join(f"cat:{c.strip()}" for c in categories if c.strip())
    params = urllib.parse.urlencode({
        "search_query": f"({query})",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": str(max_results),
    })
    url = f"{ARXIV_API}?{params}"
    last_err = None
    for attempt in range(retries + 1):
        try:
            xml_text = http_get(url)
            return parse_atom(xml_text)
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt < retries:
                import time
                time.sleep(5)
    raise RuntimeError(f"arXiv 抓取失败（已重试 {retries} 次）: {last_err}")


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def parse_atom(xml_text: str):
    root = ET.fromstring(xml_text)
    entries = []
    for e in root.findall("a:entry", ATOM_NS):
        entry_id = (e.findtext("a:id", "", ATOM_NS) or "").strip()
        m = re.search(r"abs/([0-9]+\.[0-9]+)", entry_id)
        arxiv_id = m.group(1) if m else entry_id
        authors = [_clean(a.findtext("a:name", "", ATOM_NS)) for a in e.findall("a:author", ATOM_NS)]
        published = (e.findtext("a:published", "", ATOM_NS) or "")[:10]
        cats = [c.get("term", "") for c in e.findall("a:category", ATOM_NS)]
        comment = _clean(e.findtext("ar:comment", "", ATOM_NS))
        entries.append({
            "arxiv_id": arxiv_id,
            "title": _clean(e.findtext("a:title", "", ATOM_NS)),
            "abstract": _clean(e.findtext("a:summary", "", ATOM_NS)),
            "published": published,
            "authors": authors,
            "categories": cats,
            "comment": comment,
        })
    return entries


# ---------------------------------------------------------------- 偏好画像
def load_profile(path: str) -> dict:
    """归一化偏好画像。兼容两种 schema：
    A) HANDOFF-run_daily 契约版: research_axes/frontier_boost/preferred_venues/lower_priority
    B) 现存 v0 版: weights + keywords + frontier_bonus + low_priority
    """
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    axes, boosts = [], []
    if isinstance(raw.get("research_axes"), dict):  # schema A
        for name, v in raw["research_axes"].items():
            axes.append({"name": name, "weight": float(v.get("weight", 0)),
                         "keywords": [k.lower() for k in (v.get("keywords") or [])]})
        for name, v in (raw.get("frontier_boost") or {}).items():
            boosts.append({"name": name, "boost": float(v.get("boost", 0)),
                           "keywords": [k.lower() for k in (v.get("keywords") or [])]})
        venues = raw.get("preferred_venues") or []
        low = raw.get("lower_priority") or []
    else:  # schema B（当前沙箱 v0 文件）
        weights = raw.get("weights", {})
        keywords = raw.get("keywords", {})
        for name, w in weights.items():
            axes.append({"name": name, "weight": float(w),
                         "keywords": [k.lower() for k in (keywords.get(name) or [])]})
        for name, v in (raw.get("frontier_bonus") or {}).items():
            if isinstance(v, dict):
                boosts.append({"name": name, "boost": float(v.get("boost", 0)),
                               "keywords": [k.lower() for k in (v.get("keywords") or [])]})
            elif isinstance(v, (int, float)):
                boosts.append({"name": name, "boost": float(v), "keywords": []})
        venues = []
        low = raw.get("low_priority") or []
    # frontier_bonus v0 实际结构: {name: {"boost": x, "keywords": [...]}} — 上面兜底已覆盖
    fb = raw.get("frontier_bonus") or {}
    if not boosts and isinstance(fb, dict):
        for name, v in fb.items():
            if isinstance(v, dict):
                boosts.append({"name": name, "boost": float(v.get("boost", 0)),
                               "keywords": [k.lower() for k in (v.get("keywords") or [])]})
    return {"axes": axes, "boosts": boosts, "venues": venues, "low_priority": [str(x).lower() for x in low],
            "feedback_log": raw.get("feedback_log") or []}


def score_paper(entry: dict, prof: dict):
    """返回 (score, hit_axes, hit_boosts)。双轨硬过滤由调用方按「是否命中任一轴」执行。"""
    text = (entry["title"] + " " + entry["abstract"]).lower()
    hit_axes, hit_boosts, raw = [], [], 0.0
    for ax in prof["axes"]:
        if any(k in text for k in ax["keywords"]):
            hit_axes.append(ax["name"])
            raw += ax["weight"]
    for b in prof["boosts"]:
        if any(k in text for k in b["keywords"]):
            hit_boosts.append(b["name"])
            raw += b["boost"]
    for ven in prof["venues"]:
        if ven.lower() in (entry.get("comment") or "").lower():
            raw += 0.1
            break
    low_hit = any(k in text for k in prof["low_priority"] if k)
    if low_hit:
        raw -= 0.3
    return raw, hit_axes, hit_boosts, low_hit


def normalize_score(raw: float, prof: dict) -> float:
    """命中权重占全部轴+前沿加分的比例，保留区分度；封顶 0.99。"""
    total = sum(ax["weight"] for ax in prof["axes"]) + sum(b["boost"] for b in prof["boosts"])
    if total <= 0:
        return 0.0
    return round(min(max(raw, 0) / total, 0.99), 2)


# ---------------------------------------------------------------- LLM 总结（可选）
LLM_JSON_INSTRUCTION = """你是小红书风格的论文精读博主（参考「博士侃AI」「残月魔都」的讲法）。只输出一个 JSON 对象（不要 markdown 代码块、不要多余文字）：
{
  "title_zh": "中文标题（吸引人但准确，15~25字，像帖子标题）",
  "summary": "3~5 句通俗导读：第一句场景化开场（这篇解决什么问题、为什么读者该关心），然后讲清方法核心思想，用比喻和外号讲人话，保留技术术语用反引号标注",
  "hook": "一句话钩子：最抓眼球的点（如「老办法要802秒，它只要197秒」式的对比），不超过30字",
  "cards": [
    {"emoji": "🧠", "title": "它聪明在哪", "body": "2~4 句：核心洞察/关键设计，模块可起外号+一句话解释"},
    {"emoji": "🎬", "title": "怎么做到的", "body": "2~4 句：流程怎么走，输入输出是什么"},
    {"emoji": "⚠️", "title": "也别神话它", "body": "1~3 句：诚实的局限/适用边界"}
  ],
  "category": "英文大写短标签，如 FEED-FORWARD 3D × 世界模型",
  "influence": "一句话团队/机构影响力或热度（有 HF upvote 时写明）",
  "fields": {"background":"","task":"","insight":"","pipeline":"","methods":"","experiment":"","limitation":""}
}
规则：cards 恰好 3 张；不要编造数字，摘要里的数字可以引用，没有的写「以原文为准」；fields 七键齐全（较专业表述，供深读）；summary 与 cards 面向通俗读者。"""


def _load_agent_plan_cfg():
    """读 agent_plan 配置：环境变量优先，其次 OpenClaw 平台配置文件。key 不打印不落盘副本。"""
    key = os.environ.get("AGENT_PLAN_API_KEY", "").strip()
    if key:
        return {"key": key, "base": os.environ.get("AGENT_PLAN_BASE_URL", "https://ark.cn-beijing.volces.com/api/plan/v3"),
                "model": os.environ.get("AGENT_PLAN_MODEL", "glm-5.3"), "headers": {}}
    for path in (os.path.expanduser("~/.openclaw/openclaw.json"), "/root/.openclaw/openclaw.json"):
        try:
            with open(path, encoding="utf-8") as f:
                prov = json.load(f)["models"]["providers"].get("agent_plan") or {}
            k = (prov.get("apiKey") or "").strip()
            if k.startswith("ark-"):
                mdl = prov.get("models") or []
                hdr = next((m.get("headers") for m in mdl if m.get("id") == "glm-5.3"), None) or {}
                return {"key": k, "base": prov.get("baseUrl", ""), "model": "glm-5.3", "headers": hdr}
        except Exception:  # noqa: BLE001
            continue
    return None


def _call_agent_plan(cfg, title, abstract):
    """agent_plan（OpenAI 兼容）。glm-5.3 为思考模型：reasoning 与 content 分离，max_tokens 须给足。"""
    prompt = f"{LLM_JSON_INSTRUCTION}\n\n论文标题：{title}\n摘要：{abstract}"
    body = json.dumps({
        "model": cfg["model"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000,
    }).encode("utf-8")
    req = urllib.request.Request(
        cfg["base"].rstrip("/") + "/chat/completions", data=body,
        headers={"Authorization": f"Bearer {cfg['key']}", "Content-Type": "application/json", **(cfg.get("headers") or {})})
    with urllib.request.urlopen(req, timeout=90) as r:
        out = json.loads(r.read().decode("utf-8"))
    msg = out["choices"][0]["message"]
    content = (msg.get("content") or "").strip()
    if not content:  # 思考 token 耗尽导致空 content -> 重试一次
        body = json.dumps({"model": cfg["model"], "messages": [{"role": "user", "content": prompt}],
                           "max_tokens": 8000}).encode("utf-8")
        req = urllib.request.Request(
            cfg["base"].rstrip("/") + "/chat/completions", data=body,
            headers={"Authorization": f"Bearer {cfg['key']}", "Content-Type": "application/json", **(cfg.get("headers") or {})})
        with urllib.request.urlopen(req, timeout=120) as r:
            out = json.loads(r.read().decode("utf-8"))
        content = (out["choices"][0]["message"].get("content") or "").strip()
    return _parse_llm_json(content)


def _parse_llm_json(text):
    t = text.strip()
    if t.startswith("```"):  # 去可能的代码围栏
        t = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", t).strip()
    m = re.search(r"\{.*\}", t, re.S)
    if not m:
        return None
    raw = m.group(0)
    obj = robust_parse(raw)
    if not isinstance(obj, dict) or not isinstance(obj.get("fields"), dict):
        return None
    return obj


def robust_parse(raw):
    """宽容解析截断/尾逗号/未闭合引号的 LLM JSON 输出。"""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    fixed = raw
    for _ in range(8):
        try:
            return json.loads(fixed)
        except json.JSONDecodeError as e:
            pos = e.pos
            if e.msg.startswith("Expecting ',' delimiter"):
                cut = fixed[:pos-1].rstrip().rstrip(",")
            elif e.msg.startswith("Expecting property name"):
                cut = fixed[:pos].rstrip().rstrip(",")
            elif e.msg.startswith("Unterminated string"):
                cut = fixed[:pos] + '"'
            else:
                cut = fixed[:pos].rstrip().rstrip(",")
            stack = []
            in_str = False; esc = False
            for ch in cut:
                if in_str:
                    if esc: esc = False
                    elif ch == "\\": esc = True
                    elif ch == '"': in_str = False
                else:
                    if ch == '"': in_str = True
                    elif ch in "{[": stack.append(ch)
                    elif ch == "}" and stack and stack[-1] == "{": stack.pop()
                    elif ch == "]" and stack and stack[-1] == "[": stack.pop()
            if in_str: cut += '"'
            fixed = cut + "".join("}" if c == "{" else "]" for c in reversed(stack))
    return None


def _call_deepseek(title, abstract):
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        return None
    prompt = f"{LLM_JSON_INSTRUCTION}\n\n论文标题：{title}\n摘要：{abstract}"
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions", data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.loads(r.read().decode("utf-8"))
    return _parse_llm_json(out["choices"][0]["message"]["content"])


def llm_summarize(title: str, abstract: str, provider=None):
    """总结入口：agent_plan（默认） -> DeepSeek -> None（兜底）。失败不抛异常。"""
    attempts = []
    ap_cfg = provider or _load_agent_plan_cfg()
    if ap_cfg:
        attempts.append(lambda: _call_agent_plan(ap_cfg, title, abstract))
    if os.environ.get("DEEPSEEK_API_KEY", "").strip():
        attempts.append(lambda: _call_deepseek(title, abstract))
    import time as _t
    for fn in attempts:
        for attempt in range(2):  # 每个提供商试 2 次
            try:
                out = fn()
                if out and out.get("summary"):
                    return out
                print(f"    [LLM] 返回无效（第 {attempt+1} 次），重试", file=sys.stderr)
            except Exception as e:  # noqa: BLE001
                print(f"    [LLM] 单次调用失败（{e}）第 {attempt+1} 次", file=sys.stderr)
            _t.sleep(3)
    return None


def fallback_summarize(entry: dict, category: str):
    """无 LLM 时的保守兜底：宁可留白，不编造（契约红线 1）。"""
    abstract = entry["abstract"]
    first_sent = re.split(r"(?<=[.!?])\s+", abstract)[:2]
    task_en = " ".join(first_sent)[:300]
    first_abs_sent = first_sent[0] if first_sent else abstract[:200]
    return {
        "title_zh": entry["title"][:60] + "（直译待润色）",
        "hook": "新鲜出炉：详情以原文为准",
        "summary": (f"本文属 {category} 方向。任务概述：{task_en} "
                    f"方法与实验结论以原文为准（LLM 精读后自动补全中文导读）。"),
        "cards": [
            {"emoji": "🧠", "title": "它聪明在哪",
             "body": "核心洞察待 LLM 精读补全；以原文 Abstract/Method 为准。"},
            {"emoji": "🎬", "title": "怎么做到的",
             "body": "流程与输入输出待 LLM 精读补全；以原文 Method 为准。"},
            {"emoji": "⚠️", "title": "也别神话它",
             "body": "适用边界与局限以原文 Limitation/Discussion 为准。"},
        ],
        "influence": "新论文：作者影响力标注待补充",
        "fields": {
            "background": f"arXiv 新_submission（{entry['published']}），主分类 {', '.join(entry['categories'][:3])}。",
            "task": task_en or "以原文 Abstract 为准。",
            "insight": "核心洞察以原文 Abstract/Method 为准（待 LLM 精读补全）。",
            "pipeline": "I/O 与模块拆解待 LLM 精读填充；以原文 Method 部分与流程图为准。",
            "methods": "方法细节以原文为准。",
            "experiment": "实验数据集与消融详见原文 Experiments（数字以原文为准）。",
            "limitation": "局限以原文 Limitation/Discussion 为准。",
        },
    }


# ---------------------------------------------------------------- 主流程
def main():
    ap = argparse.ArgumentParser(description="每日论文精选检索管道 v0.2")
    ap.add_argument("--categories", default="cs.CV,cs.AI,cs.LG,cs.RO")
    ap.add_argument("--max", type=int, default=8, help="精选篇数（5~8，默认 8）")
    ap.add_argument("--fetch-limit", type=int, default=200, help="arXiv 抓取条数")
    ap.add_argument("--window-days", type=int, default=120, help="时间窗：最近 N 天都算新论文")
    ap.add_argument("--sources-extra", action="store_true", default=True, help="拉取 HF 热度数据（hf-mirror）")
    ap.add_argument("--no-sources-extra", dest="sources_extra", action="store_false")
    ap.add_argument("--llm-top", type=int, default=12, help="送 LLM 总结的候选篇数")
    ap.add_argument("--profile", default=PROFILE_PATH)
    ap.add_argument("--dry-run", action="store_true", help="只产出 today.json，不调用 build_web_data、不覆盖 web/data.js")
    args = ap.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)
    prof = load_profile(args.profile)
    cats = [c.strip() for c in args.categories.split(",") if c.strip()]

    # 1) 抓取（失败则保留上期产物并退出）
    print(f"[1/5] 抓取 arXiv: cats={cats} limit={args.fetch_limit} window={args.window_days}d")
    try:
        entries = fetch_arxiv(cats, args.fetch_limit)
    except RuntimeError as e:
        print(f"[!] {e}")
        print("[!] 按红线 5：保留上期 data/today.json 与 web/data.js 不覆盖，今日跳过。")
        sys.exit(1)
    print(f"    共 {len(entries)} 条")

    # 1b) 扩展源：HF daily papers 热度（upvote>=30 写入 influence；热度加成 +0.08）
    hf_hot, hf_all = {}, {}
    if args.sources_extra:
        se_path = os.path.join(DATA_DIR, "sources_extra.json")
        try:
            subprocess.run([sys.executable, os.path.join(BASE_DIR, "sources_extra.py")], capture_output=True, timeout=240)
            with open(se_path, encoding="utf-8") as f:
                se = json.load(f)
            hf_all = se.get("hf_daily") or {}
            hf_hot = se.get("hf_hot") or {}
            print(f"    [HF] 热度数据：{len(hf_all)} 篇（热门 {len(hf_hot)}）")
        except Exception as e:  # noqa: BLE001
            print(f"    [HF] 扩展源失败（{e}），继续仅用 arXiv", file=sys.stderr)

    # 1c) 中文媒体源（公众号/B站）：热度信号 + 论文关联
    media_hot = {}   # arxiv_id -> [ {source,title,url} ]
    media_kw_hot = []  # 标题关键词命中列表（英文论文名出现在中文标题里）
    try:
        mm_path = os.path.join(DATA_DIR, "media_mentions.json")
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "media_monitor.py")], capture_output=True, timeout=500)
        with open(mm_path, encoding="utf-8") as f:
            mm = json.load(f)
        for mention in mm.get("mentions") or []:
            aid = mention.get("arxiv_id")
            if aid:
                media_hot.setdefault(aid, []).append(mention)
            media_kw_hot.append(mention)
        print(f"    [媒体] 公众号/B站提及 {len(mm.get('mentions') or [])} 条（含 arXiv ID {len(media_hot)} 条）")
    except Exception as e:  # noqa: BLE001
        print(f"    [媒体] 扩展源失败（{e}），继续", file=sys.stderr)

    def media_signal(e):
        """论文在中文社区的提及信号：arXiv ID 直接命中 + 英文标题词命中中文标题。"""
        sig = 0.0
        hits = list(media_hot.get(e["arxiv_id"], []))
        title_words = [w for w in re.findall(r"[A-Za-z]{5,}", e["title"]) if w.lower() not in
                       ("about", "using", "towards", "model", "models", "learning", "based", "with")]
        for m in media_kw_hot:
            t = (m.get("title") or "") + (m.get("summary") or "")
            if any(w in t for w in title_words[:6]):
                hits.append(m)
        if hits:
            sig = min(0.10, 0.05 * len(hits))
        return sig, hits

    # 2) 时间窗 + 偏好轴硬过滤 + 偏门方向排除
    cutoff = (datetime.date.today() - datetime.timedelta(days=args.window_days)).isoformat()
    try:
        import importlib
        se_mod = importlib.import_module("sources_extra") if os.path.dirname(os.path.join(BASE_DIR, "sources_extra.py")) == BASE_DIR else None
        exclude_kws = se_mod.EXCLUDE_KEYWORDS if se_mod else []
    except Exception:  # noqa: BLE001
        exclude_kws = []
    if not exclude_kws:
        try:
            sys.path.insert(0, BASE_DIR)
            from sources_extra import EXCLUDE_KEYWORDS as _ek  # noqa
            exclude_kws = _ek
        except Exception:  # noqa: BLE001
            exclude_kws = []
    cands = []
    skipped_window = skipped_excl = 0
    for e in entries:
        if not e["title"] or not e["abstract"]:
            continue
        if e["published"] < cutoff:
            skipped_window += 1
            continue
        text_low = (e["title"] + " " + e["abstract"]).lower()
        if any(k in text_low for k in exclude_kws):
            skipped_excl += 1
            continue
        score, hit_axes, hit_boosts, low_hit = score_paper(e, prof)
        if not hit_axes:
            continue
        if low_hit and max((ax["weight"] for ax in prof["axes"] if ax["name"] in hit_axes), default=0) < 0.9:
            continue
        hf_bonus = 0.08 if e["arxiv_id"] in hf_hot else 0.0
        med_bonus, med_hits = media_signal(e)
        cands.append({**e, "_score": round(normalize_score(score, prof) + hf_bonus + med_bonus, 2), "_axes": hit_axes,
                      "_boosts": hit_boosts, "_hf_up": hf_hot.get(e["arxiv_id"], {}).get("upvotes", 0),
                      "_media_hits": med_hits[:3]})
    cands.sort(key=lambda x: (x["_score"], x["_hf_up"]), reverse=True)
    print(f"[2/5] 粗筛：窗口外剔除 {skipped_window}，偏门排除 {skipped_excl}，命中偏好轴候选 {len(cands)} 篇")

    if not cands:
        print("[!] 今日窗口内无合适论文 -> 写入「今日无精选」而非退出。")
        today = datetime.date.today()
        empty = {"issue": f"No.{today.strftime('%j')}", "date": today.isoformat(),
                 "axes": AXES_TITLE, "empty": True, "reason": "今日时间窗内无命中偏好方向的合适论文",
                 "papers": []}
        with open(TODAY_JSON, "w", encoding="utf-8") as f:
            json.dump(empty, f, ensure_ascii=False, indent=2)
        if not args.dry_run:
            subprocess.run([sys.executable, BUILD_SCRIPT, "--input", TODAY_JSON,
                            "--output", os.path.join(ROOT, "web", "data.js"),
                            "--issue", f"No.{today.strftime('%j')}", "--date", today.isoformat(),
                            "--axes", AXES_TITLE,
                            "--ed-note", "今日窗口内无合适论文，明天见。"], capture_output=True, text=True)
        print("[!] 已写空状态 today.json / data.js")
        sys.exit(0)

    # 3) LLM 总结（top N；agent_plan -> DeepSeek -> 兜底）
    ap_cfg = _load_agent_plan_cfg()
    has_key = bool(ap_cfg or os.environ.get("DEEPSEEK_API_KEY", "").strip())
    src = "agent_plan(glm-5.3)" if ap_cfg else ("DeepSeek" if has_key else "无任何 LLM key -> 保守兜底")
    print(f"[3/5] 总结 top {min(args.llm_top, len(cands))} 篇（{src}）")
    papers = []
    for e in cands[:args.llm_top]:
        category = e["_axes"][0] + (f" × {e['_axes'][1]}" if len(e["_axes"]) > 1 else "")
        llm = llm_summarize(e["title"], e["abstract"], provider=ap_cfg) if has_key else None
        info = llm or fallback_summarize(e, category)
        if llm:
            category = llm.get("category") or category
        first_author = (e["authors"] or ["佚名"])[0]
        authors_disp = first_author + (" et al." if len(e["authors"]) > 1 else "")
        venue = f"arXiv {e['published'][:7].replace('-', '.')}"
        if e["comment"]:
            venue += f" · {e['comment'][:60]}"
        influence = info.get("influence", "") or ""
        if e.get("_hf_up"):
            influence = f"HF upvote {e['_hf_up']} · " + influence
        if e.get("_media_hits"):
            srcs = "、".join(sorted({("公众号" if h["source"] == "weixin" else "B站") for h in e["_media_hits"]}))
            influence = f"中文社区 {srcs} 热议 · " + influence
        papers.append({
            "title": e["title"],
            "title_zh": (info.get("title_zh") or "") if isinstance(info, dict) else "",
            "hook": (info.get("hook") or "") if isinstance(info, dict) else "",
            "cards": (info.get("cards") or []) if isinstance(info, dict) else [],
            "authors": authors_disp,
            "venue": venue,
            "summary": info["summary"],
            "paper_url": f"https://arxiv.org/abs/{e['arxiv_id']}",
            "score": e["_score"],
            "category": category,
            "influence": influence,
            "figure_url": None,  # 红线 2：简洁无图
            "figure_caption": "",
            "fields": {k: (info.get("fields", {}).get(k, "") or "") for k in
                       ("background", "task", "insight", "pipeline", "methods", "experiment", "limitation")},
            "_boosts": e["_boosts"],
        })
    # 4) 取 top max 篇写 today.json（list 格式，契约第五节）
    chosen = papers[: args.max]
    for p in chosen:
        p.pop("_boosts", None)
    with open(TODAY_JSON, "w", encoding="utf-8") as f:
        json.dump(chosen, f, ensure_ascii=False, indent=2)
    print(f"[4/5] 写出 {TODAY_JSON}（{len(chosen)} 篇，score 最高: {chosen[0]['title'][:48]}… -> hero）")

    if args.dry_run:
        print("[dry-run] 到此为止：未调用 build_web_data.py，web/data.js 未动。")
        return

    print("[5/5] 生成网页数据 ...")

    today = datetime.date.today()
    cmd = [sys.executable, BUILD_SCRIPT,
           "--input", TODAY_JSON,
           "--output", os.path.join(ROOT, "web", "data.js"),
           "--issue", f"No.{today.strftime('%j')}",
           "--date", today.isoformat(),
           "--axes", AXES_TITLE,
           "--ed-note", "本期精选基于偏好画像筛选与排序。"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr.strip(), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
