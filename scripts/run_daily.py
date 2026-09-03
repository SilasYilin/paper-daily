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
# 直连 opener（环境 http_proxy 若指向不存在的本地代理，urlopen 会连接被拒）
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def http_get(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "paper-daily/0.2 (research digest; contact: none)"})
    with _OPENER.open(req, timeout=timeout) as r:
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


def fetch_arxiv_by_ids(ids):
    """按 arXiv ID 批量补抓元数据（AI HOT 池内独有论文用）。"""
    params = urllib.parse.urlencode({"id_list": ",".join(ids), "max_results": str(len(ids))})
    xml_text = http_get(f"{ARXIV_API}?{params}")
    return parse_atom(xml_text)


def _norm_title(s: str) -> str:
    """标题归一化（小写、去非字母数字），用于跨源标题模糊对齐。"""
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


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
LLM_JSON_INSTRUCTION = """你是论文精读卡片作者。只输出一个 JSON 对象（不要 markdown 代码块、不要多余文字）：
{
  "title_zh": "中文标题（准确、有吸引力，15~25字）",
  "summary": "通俗导读 3~4 句：第一句用生活化场景讲这篇解决什么问题（像跟同学聊天），其余讲核心思想，可用比喻；技术术语用反引号标注",
  "hook": "一句话钩子：最抓眼球的点，不超过30字",
  "cards": [
    {"emoji": "🎯", "title": "问题与背景", "body": "专业表述：研究问题、已有方法的两难、为什么难（3~5 句，学术语气）"},
    {"emoji": "⚙️", "title": "方法设计", "body": "专业表述：核心方法与关键模块拆解，模块名用反引号（4~6 句）"},
    {"emoji": "📊", "title": "实验结果", "body": "专业表述：数据集、指标、与 SOTA 对比（3~5 句；数字必须来自摘要，没有就写「详见原文」）"},
    {"emoji": "⚠️", "title": "局限与展望", "body": "专业表述：作者承认的局限+你判断的边界（2~4 句）"}
  ],
  "category": "英文大写短标签，如 FEED-FORWARD 3D × 世界模型",
  "scores": {"innovation": 0, "effectiveness": 0},
  "influence": "一句话团队/机构影响力或热度",
  "figure_note": "流程图解说：假设流程图展示了方法全景，用 2~3 句专业语气解释图里各模块如何衔接（供流程图卡片配文，若摘要无信息则写「以原文流程图为准」）",
  "fields": {"background":"","task":"","insight":"","pipeline":"","methods":"","experiment":"","limitation":""}
}
规则：cards 恰好 4 张，顺序固定（问题背景/方法设计/实验结果/局限展望）；summary 是通俗体、cards 与 fields 是专业体，两种语气不要混；不编造数字，摘要里的数字才可引用；fields 七键齐全；
scores 从两个角度打分（0~10 整数）：innovation=创新（问题定义/思想/框架的新颖度），effectiveness=效果（实验验证的强度与提升幅度）；仅依据摘要证据打分，宁可保守不虚高；两者独立，不要为平衡而拉齐。"""


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
        "max_tokens": 9000,
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
                           "max_tokens": 14000}).encode("utf-8")
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
    if not isinstance(obj, dict):
        return None
    has_cards = isinstance(obj.get("cards"), list) and len(obj["cards"]) >= 3
    has_fields = isinstance(obj.get("fields"), dict)
    if not (has_cards or (has_fields and obj.get("summary"))):
        return None
    if not has_fields:
        obj["fields"] = {}
    if not has_cards and not obj.get("cards"):
        obj["cards"] = []
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
            {"emoji": "🎯", "title": "问题与背景",
             "body": "研究问题与背景以原文 Abstract/Introduction 为准（LLM 精读后补全专业表述）。"},
            {"emoji": "⚙️", "title": "方法设计",
             "body": "方法与模块拆解以原文 Method 为准（待 LLM 精读补全）。"},
            {"emoji": "📊", "title": "实验结果",
             "body": "数据集、指标与 SOTA 对比详见原文 Experiments（数字以原文为准）。"},
            {"emoji": "⚠️", "title": "局限与展望",
             "body": "局限以原文 Limitation/Discussion 为准。"},
        ],
        "figure_note": "以原文流程图为准。",
        "scores": {"innovation": None, "effectiveness": None, "note": "LLM 未运行，评分待补"},
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
    ap.add_argument("--no-figures", action="store_true", help="不抓流程图（默认抓）")
    ap.add_argument("--llm-top", type=int, default=12, help="送 LLM 总结的候选篇数")
    ap.add_argument("--profile", default=PROFILE_PATH)
    ap.add_argument("--dry-run", action="store_true", help="只产出 today.json，不调用 build_web_data、不覆盖 web/data.js")
    args = ap.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)
    prof = load_profile(args.profile)
    cats = [c.strip() for c in args.categories.split(",") if c.strip()]

    # 1) 抓取（v0.9 源优先级：HF daily papers 主源 -> arXiv 元数据补抓/兜底）
    print(f"[1/5] 抓取：HF daily(7d) 主源 + arXiv(cats={cats}, limit={args.fetch_limit}) 补抓")
    hf_main = {}
    try:
        import importlib
        sh = importlib.import_module("sources_hf") if BASE_DIR in sys.path else None
        if sh is None:
            sys.path.insert(0, BASE_DIR)
            import sources_hf as sh  # noqa
        sh.main()
        with open(os.path.join(DATA_DIR, "sources_hf.json"), encoding="utf-8") as f:
            hf_main = json.load(f).get("hf_daily") or {}
        print(f"    [HF主源] {len(hf_main)} 篇（含 githubRepo {sum(1 for v in hf_main.values() if v.get('githubRepo'))} 篇）")
    except Exception as e:  # noqa: BLE001
        print(f"    [HF主源] 拉取失败（{e}），退回 arXiv 主源")
    try:
        entries = fetch_arxiv(cats, args.fetch_limit)
    except RuntimeError as e:
        entries = []
        if not hf_main:
            print(f"[!] arXiv 也失败：{e}")
            print("[!] 按红线 5：保留上期 data/today.json 与 web/data.js 不覆盖，今日跳过。")
            sys.exit(1)
        print("    [arXiv] 失败，仅用 HF 主源候选")
    hf_ids = set(hf_main)
    # 1a-2) AI HOT 中文策展池（aihot skill 通道）：热度信号 + 池内独有论文补抓元数据
    aihot_signals, aihot_title_map = {}, {}
    try:
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "sources_aihot.py")],
                       capture_output=True, timeout=300)
        with open(os.path.join(DATA_DIR, "sources_aihot.json"), encoding="utf-8") as f:
            ah = json.load(f)
        aihot_signals = ah.get("signals") or {}
        for c in ah.get("curated") or []:
            for t in (c.get("originalTitle"), c.get("title")):
                nt = _norm_title(t or "")
                if len(nt) >= 12:
                    aihot_title_map[nt] = max(aihot_title_map.get(nt, 0), 0.08)
        for kwh in ah.get("kw_hits") or []:
            w = 0.06 if kwh.get("mode") == "selected" else 0.02
            for c in kwh.get("items") or []:
                for t in (c.get("originalTitle"), c.get("title")):
                    nt = _norm_title(t or "")
                    if len(nt) >= 12:
                        aihot_title_map[nt] = max(aihot_title_map.get(nt, 0), w)
        print(f"    [AIHOT] 精选池 {len(ah.get('curated') or [])} 条，信号覆盖 {len(aihot_signals)} 个 arXiv ID")
    except Exception as e:  # noqa: BLE001
        print(f"    [AIHOT] 拉取失败（{e}），跳过", file=sys.stderr)
    merged = {e["arxiv_id"]: e for e in entries}
    for aid, v in hf_main.items():
        if aid not in merged:
            merged[aid] = {
                "arxiv_id": aid, "title": v.get("title") or "",
                "abstract": "", "authors": "", "published": (v.get("publishedAt") or "")[:10],
                "categories": [], "comment": "", "_from_hf": True, "_hf_up": v.get("upvotes", 0),
                "_github": v.get("githubRepo") or "",
            }
        else:
            merged[aid]["_from_hf"] = True
            merged[aid]["_hf_up"] = max(merged[aid].get("_hf_up", 0), v.get("upvotes", 0))
            if v.get("githubRepo"):
                merged[aid]["_github"] = v["githubRepo"]
    entries = list(merged.values())
    # AI HOT 池内独有论文：批量补抓 arXiv 元数据后并入候选
    missing_ai = [a for a in aihot_signals if a not in merged]
    if missing_ai:
        try:
            got = fetch_arxiv_by_ids(missing_ai[:25])
            for e2 in got:
                merged[e2["arxiv_id"]] = {**e2, "_from_aihot": True}
            entries = list(merged.values())
            print(f"    [AIHOT] 池内独有 {len(missing_ai)} 篇，补抓到 arXiv 元数据 {len(got)} 篇")
        except Exception as ex:  # noqa: BLE001
            print(f"    [AIHOT] arXiv 元数据补抓失败（{ex}）", file=sys.stderr)
    print(f"    合并后共 {len(entries)} 条（HF {len(hf_ids)} + arXiv 独有 {len(entries) - len([e for e in entries if e.get('_from_hf')])}）")

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

    # 1c) 中文媒体源（公众号）：wechat-article-search skill 通道优先，失败回退 opencli media_monitor
    media_hot = {}   # arxiv_id -> [ {source,title,url} ]
    media_kw_hot = []  # 标题关键词命中列表（英文论文名出现在中文标题里）
    try:
        mm_path = os.path.join(DATA_DIR, "media_mentions.json")
        ok_mm = False
        for mm_script in ("sources_wechat.py", "media_monitor.py"):
            try:
                r_mm = subprocess.run([sys.executable, os.path.join(BASE_DIR, mm_script)],
                                      capture_output=True, timeout=500)
                if r_mm.returncode == 0:
                    ok_mm = True
                    break
            except Exception:  # noqa: BLE001
                continue
        if ok_mm:
            with open(mm_path, encoding="utf-8") as f:
                mm = json.load(f)
            for mention in mm.get("mentions") or []:
                aid = mention.get("arxiv_id")
                if aid:
                    media_hot.setdefault(aid, []).append(mention)
                media_kw_hot.append(mention)
            print(f"    [媒体] 公众号提及 {len(mm.get('mentions') or [])} 条（含 arXiv ID {len(media_hot)} 条）")
        else:
            print("    [媒体] 两个通道都失败，今日无媒体信号", file=sys.stderr)
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
        hf_bonus = 0.10 if e.get("_from_hf") else 0.0  # v0.9：入选 HF daily 本身是社区筛选信号
        hf_bonus += min(0.10, (e.get("_hf_up", 0) or 0) / 300.0)  # upvote 热度：300 票封顶 +0.10
        hf_bonus += 0.08 if e["arxiv_id"] in hf_hot else 0.0
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
            srcs = "、".join(sorted({(h.get("account") or ("公众号" if h.get("source") == "weixin" else "B站"))
                                     for h in e["_media_hits"]}))
            influence = f"中文社区 {srcs} 热议 · " + influence
        if e.get("_aihot_w"):
            influence = "AI HOT 中文社区收录 · " + influence
        figure_note = (info.get("figure_note") or "以原文流程图为准。") if isinstance(info, dict) else "以原文流程图为准。"
        # 双维度评分（0~10）：LLM 打分；无则按启发式保守估计并标注
        sc = (info.get("scores") or {}) if isinstance(info, dict) else {}
        def _clamp10(v):
            try:
                iv = int(round(float(v)))
                return iv if 0 <= iv <= 10 else None
            except (TypeError, ValueError):
                return None
        scores_obj = {"innovation": _clamp10(sc.get("innovation")), "effectiveness": _clamp10(sc.get("effectiveness"))}
        if scores_obj["innovation"] is None or scores_obj["effectiveness"] is None:
            # 具名元组无法导入，直接启发式：偏门排除过后命中偏好轴>=2 或有 HF/媒体热度的保守 7 分档
            est = 7 if (len(e.get("_axes") or []) >= 2 or e.get("_hf_up") or e.get("_media_hits")) else 6
            scores_obj = {"innovation": scores_obj["innovation"] if scores_obj["innovation"] is not None else est,
                          "effectiveness": scores_obj["effectiveness"] if scores_obj["effectiveness"] is not None else est,
                          "note": "启发式估计（LLM 未出分），仅供参考"}
        figures = []
        if not args.no_figures:
            try:
                from fetch_figures import fetch_figures as _ff
                figures = _ff(e["arxiv_id"], top_k=1)
            except Exception as fe:  # noqa: BLE001
                print(f"    [fig] {e['arxiv_id']} 流程图抓取失败：{fe}", file=sys.stderr)
        papers.append({
            "title": e["title"],
            "title_zh": (info.get("title_zh") or "") if isinstance(info, dict) else "",
            "hook": (info.get("hook") or "") if isinstance(info, dict) else "",
            "cards": (info.get("cards") or []) if isinstance(info, dict) else [],
            "figure_note": figure_note,
            "figures": figures,
            "authors": authors_disp,
            "venue": venue,
            "summary": info["summary"],
            "paper_url": f"https://arxiv.org/abs/{e['arxiv_id']}",
            "score": e["_score"],
            "scores": scores_obj,
            "category": category,
            "influence": influence,
            "figure_url": figures[0]["file"] if figures else None,
            "figure_caption": figures[0]["caption"] if figures else "",
            "fields": {k: (info.get("fields", {}).get(k, "") or "") for k in
                       ("background", "task", "insight", "pipeline", "methods", "experiment", "limitation")},
            "_boosts": e["_boosts"],
        })
    # 4) 取 top max 篇写 today.json（list 格式，契约第五节）
    chosen = papers[: args.max]
    # v0.9：封面元数据补全（作者/高校/被引/star/GitHub）——只对最终精选的少量论文请求
    try:
        sys.path.insert(0, BASE_DIR)
        import paper_meta
        _repos = {e["arxiv_id"]: e.get("_github") or "" for e in cands[: args.llm_top] if e["arxiv_id"] in {p_["paper_url"].rsplit("/", 1)[-1] for p_ in chosen}}
        paper_meta.enrich(chosen_mapped := [{"arxiv_id": p_["paper_url"].rsplit("/", 1)[-1], **p_} for p_ in chosen], _repos)
        for src_, dst_ in zip(chosen_mapped, chosen):
            for k in ("cited_by", "institutions", "github", "stars"):
                if src_.get(k) is not None:
                    dst_[k] = src_[k]
            # 高校并入 authors 展示字段
            if src_.get("institutions"):
                dst_["authors"] = src_["authors"] + " · " + " / ".join(src_["institutions"])
    except Exception as me:  # noqa: BLE001
        print(f"    [meta] 元数据补全失败（不阻塞）：{me}", file=sys.stderr)
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
