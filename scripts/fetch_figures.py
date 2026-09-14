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
import net  # noqa: E402  自适应网络层

_OPENER = net  # 自适应代理/直连（net.py）

BASE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(os.path.dirname(BASE), "web", "figs")
PIPELINE_WORDS = ["pipeline", "overview", "framework", "method", "architecture", "approach", "model overview"]


MAX_W = 1600          # 输出最大宽度
QUALITY = 80          # JPEG 质量
COMPRESS_MIN = 150_000  # 超过此体积才压缩（小图保持原样，避免无谓重编码）


def _compress(raw: bytes, fname: str, arxiv_id: str, idx: int):
    """把位图压成受控体积的 JPEG。Pillow 不可用时打印告警并返回原图，不再静默吞异常。"""
    if len(raw) <= COMPRESS_MIN:
        return raw, fname, os.path.join(WEB, fname)
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(raw))
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        elif im.mode == "L":
            im = im.convert("RGB")
        if im.width > MAX_W:
            im = im.resize((MAX_W, max(1, int(im.height * MAX_W / im.width))), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=QUALITY, optimize=True, progressive=True)
        out = buf.getvalue()
        # 压完反而更大（极少数已高度优化的图）就保留原图
        if len(out) >= len(raw):
            return raw, fname, os.path.join(WEB, fname)
        new_fname = f"{arxiv_id.replace('.', '_')}-fig{idx}.jpg"
        print(f"    [fig] 压缩 {len(raw)//1024}KB → {len(out)//1024}KB ({im.width}px)")
        return out, new_fname, os.path.join(WEB, new_fname)
    except ImportError:
        print("    [fig] 警告：未安装 Pillow，图片未压缩（pip install Pillow）", file=sys.stderr)
        return raw, fname, os.path.join(WEB, fname)
    except Exception as e:  # noqa: BLE001
        print(f"    [fig] 压缩失败，保留原图：{type(e).__name__} {e}", file=sys.stderr)
        return raw, fname, os.path.join(WEB, fname)


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
            # 尺寸控制：位图统一压到 JPEG（宽 ≤1600，quality 80）。
            # 阈值 150KB —— 论文原图常达 3MB+，不压会把仓库撑爆（2026-09-14 实测）。
            if ext in (".png", ".jpg", ".jpeg", ".webp"):
                raw, fname, path = _compress(raw, fname, arxiv_id, len(chosen) + 1)
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
