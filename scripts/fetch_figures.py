#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_figures.py - 从 arXiv HTML 版抓论文流程图（v0.5）

策略：
  1. GET https://arxiv.org/html/<id>（LaTeXML 渲染版）
  2. 解析 <figure> 里的 <img src> + <figcaption>
  3. caption 命中 pipeline/overview/framework/method/architecture 等词的优先
  4. 下载图片到 web/figs/<id>-fig<k>.<ext>，返回 [{url, caption, kind}]
红线：图片仅用于论文流程图卡片（用户 2026-08-29 指示），不存全文图片。
"""
import os
import re
import sys
import urllib.request

# 直连 opener（绕过可能失效的本地 http_proxy 环境变量）
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

BASE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(os.path.dirname(BASE), "web", "figs")
PIPELINE_WORDS = ["pipeline", "overview", "framework", "method", "architecture", "approach", "model overview"]


def fetch_figures(arxiv_id, top_k=1):
    os.makedirs(WEB, exist_ok=True)
    url = f"https://arxiv.org/html/{arxiv_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "paper-daily/0.5"})
    with _OPENER.open(req, timeout=30) as r:
        html = r.read().decode("utf-8", errors="ignore")

    out = []
    # 逐个 figure 解析（figure 内含 img + figcaption）
    for m in re.finditer(r"<figure[^>]*>(.*?)</figure>", html, re.S):
        block = m.group(1)
        img = re.search(r'<img[^>]+src="([^"]+)"', block)
        cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", block, re.S)
        if not img:
            continue
        src = img.group(1)
        if src.startswith("/static/"):
            continue  # arXiv 站点图标
        if not src.startswith("http"):
            src = f"https://arxiv.org/html/{src}" if not src.startswith(arxiv_id) else f"https://arxiv.org/html/{src}"
        caption = re.sub(r"<[^>]+>", " ", cap.group(1)).strip() if cap else ""
        caption = re.sub(r"\s+", " ", caption)[:200]
        low = caption.lower()
        kind = "pipeline" if any(w in low for w in PIPELINE_WORDS) else "other"
        out.append({"src": src, "caption": caption, "kind": kind})

    # pipeline 图优先，其次第一张 figure（通常是 teaser/overview）
    out.sort(key=lambda x: (0 if x["kind"] == "pipeline" else 1))
    chosen = []
    seen_cap = set()
    for f in out:
        if len(chosen) >= top_k:
            break
        key = f["src"].split("/")[-1]
        if key in seen_cap:
            continue
        seen_cap.add(key)
        ext = os.path.splitext(f["src"])[1] or ".png"
        if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
            ext = ".png"
        if ext == ".svg":
            ext = ".png"  # arXiv 的 svg 少见，下载后尝试转换，失败即弃
        fname = f"{arxiv_id.replace('.', '_')}-fig{len(chosen)+1}{ext}"
        path = os.path.join(WEB, fname)
        try:
            req = urllib.request.Request(f["src"], headers={"User-Agent": "paper-daily/0.5"})
            with _OPENER.open(req, timeout=30) as r:
                raw = r.read()
            # 尺寸控制：>1.2MB 或宽>2000 用 Pillow 压到 JPEG/缩放
            if ext in (".png", ".jpg", ".jpeg") and len(raw) > 300_000:
                try:
                    from PIL import Image
                    import io
                    im = Image.open(io.BytesIO(raw)).convert("RGB")
                    if im.width > 2000:
                        im = im.resize((2000, int(im.height * 2000 / im.width)), Image.LANCZOS)
                    buf = io.BytesIO()
                    im.save(buf, format="JPEG", quality=82)
                    raw = buf.getvalue()
                    fname = fname.rsplit(".", 1)[0] + ".jpg"
                    path = os.path.join(WEB, fname)
                except Exception:  # noqa: BLE001
                    pass
            with open(path, "wb") as w:
                w.write(raw)
            chosen.append({"file": fname, "caption": f["caption"], "kind": f["kind"]})
        except Exception as e:  # noqa: BLE001
            print(f"    [fig] {f['src']} 下载失败: {e}", file=sys.stderr)
    return chosen


if __name__ == "__main__":
    aid = sys.argv[1] if len(sys.argv) > 1 else "2608.26809"
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    import json
    print(json.dumps(fetch_figures(aid, k), ensure_ascii=False, indent=1))
