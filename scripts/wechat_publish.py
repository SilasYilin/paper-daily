#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wechat_publish.py - 「每日论文精选」公众号发布脚本 v0.2（仅入库草稿版）

依据 HANDOFF-v2（2026-08-27 23:36）公众号约束：
- 个人订阅号（未认证）：freepublish 已被微信回收（2025-07 新政）-> 永久不可自动发布
- 可用接口：token / 素材管理 / 草稿箱 draft/add -> 本脚本只写草稿，群发由用户在后台手动点（≈10秒，也是安全缓冲）
- 公众号外链图片会被拦截 -> 默认 --no-figures 纯文本
- draft/add 强制要封面 thumb_media_id -> 用户先在素材库传品牌封面拿 media_id，之后复用

凭证：环境变量 WECHAT_APPID / WECHAT_SECRET（用户本人获取，存本地 .env，勿硬编码勿外传）
IP 白名单：运行机公网出口 IP 必须加进 mp.weixin.qq.com 基本配置（本沙箱: 101.96.230.16），否则 40164

用法:
  python wechat_publish.py --html-only                     # 无凭证: 生成可粘贴 HTML（默认安全模式）
  python wechat_publish.py --dry-run                       # 有凭证: 演练，不真正调微信 API
  python wechat_publish.py --thumb-media-id XXX            # 真实写草稿箱（需凭证+封面id）
"""
import argparse, json, os, html, datetime, time
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
DATA = os.path.join(ROOT, "data", "today.json")
OUT = os.path.join(BASE_DIR, "output")

WX_BASE = "https://api.weixin.qq.com/cgi-bin"


def http_json(url, data=None, timeout=30):
    if data is not None:
        req = urllib.request.Request(
            url,
            data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
    else:
        req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def get_token(appid, secret):
    url = f"{WX_BASE}/token?grant_type=client_credential&appid={appid}&secret={secret}"
    d = http_json(url)
    if "access_token" not in d:
        errcode = d.get("errcode")
        if errcode == 40164:
            raise RuntimeError(f"40164 IP 不在白名单: {d.get('errmsg','')} -> 请把出口IP加进公众号基本配置IP白名单")
        raise RuntimeError(f"获取token失败: {d}")
    return d["access_token"]


def esc(s):
    return html.escape(str(s or ""))


def build_article_html(doc, no_figures=True):
    """today.json -> 公众号图文正文 HTML（内联样式，纯文本无图版为默认）"""
    papers = doc.get("papers", [])
    date_str = doc.get("date", datetime.date.today().isoformat())
    sections = []
    for p in papers:
        f = p.get("fields", {})
        fig_html = ""
        if not no_figures and p.get("figure_url"):
            fig_html = f'<p style="text-align:center;color:#999;font-size:12px;">[图: {esc(p.get("figure_caption", ""))}]</p>'
        sec = f"""
<section style="background:#fff;border:1px solid #eee;border-radius:12px;padding:18px;margin:12px 0;">
  <h2 style="font-size:17px;color:#111;margin:0 0 4px;">{esc(p["title"])}</h2>
  <p style="color:#888;font-size:12px;margin:0 0 8px;">{esc(p.get("authors", ""))[:120]} · {esc(p.get("venue", "arXiv"))} · 相关度 {p.get("score", "")}</p>
  <p style="color:#333;font-size:14px;line-height:1.75;margin:10px 0;"><b style="color:#c0392b;">AI 导读</b>：{esc(p.get("summary", ""))}</p>
  {fig_html}
  <p style="color:#57606a;font-size:13px;line-height:1.8;">
  <b>Background</b>：{esc(f.get("background", ""))}<br/>
  <b>Task</b>：{esc(f.get("task", ""))}<br/>
  <b>Insight</b>：{esc(f.get("insight", ""))}<br/>
  <b>Pipeline</b>：{esc(f.get("pipeline", ""))}<br/>
  <b>Methods</b>：{esc(f.get("methods", ""))}<br/>
  <b>Experiment</b>：{esc(f.get("experiment", ""))}<br/>
  <b>Limitation</b>：{esc(f.get("limitation", ""))}</p>
  <p style="font-size:12px;"><a href="{esc(p.get("paper_url", ""))}" style="color:#0969da;">论文原文 -></a></p>
</section>"""
        sections.append(sec)
    body = "\n".join(sections)
    return f"""<section style="font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;max-width:100%;">
<h1 style="font-size:20px;color:#111;">每日论文精选 · {date_str}</h1>
<p style="color:#666;font-size:13px;">三维重建 × World Model 方向 · {len(papers)} 篇 · 每日更新</p>
{body}
<p style="color:#999;font-size:12px;margin-top:16px;">由论文日报管家自动生成，仅供个人科研参考。偏好反馈请直接回复留言。</p>
</section>"""


def add_draft(token, title, content_html, thumb_media_id, digest=""):
    """创建草稿（仅入库草稿箱，不发布）。draft/add 强制要封面 thumb_media_id。"""
    body = {
        "articles": [{
            "title": title,
            "author": "论文日报管家",
            "digest": digest,
            "content": content_html,
            "content_source_url": "",
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0,
        }]
    }
    d = http_json(f"{WX_BASE}/draft/add?access_token={token}", data=body)
    if "media_id" not in d:
        raise RuntimeError(f"创建草稿失败: {d}")
    return d["media_id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html-only", action="store_true", help="无凭证模式: 只生成可粘贴HTML")
    ap.add_argument("--dry-run", action="store_true", help="有凭证演练: 走到token检查为止, 不写草稿")
    ap.add_argument("--no-figures", action="store_true", default=True, help="纯文本无图(默认, 公众号外链图会被拦截)")
    ap.add_argument("--with-figures", dest="no_figures", action="store_false", help="保留图位标注")
    ap.add_argument("--thumb-media-id", default=os.environ.get("WECHAT_THUMB_MEDIA_ID", ""), help="封面素材media_id(draft/add必填, 复用)")
    ap.add_argument("--appid", default=os.environ.get("WECHAT_APPID", ""))
    ap.add_argument("--secret", default=os.environ.get("WECHAT_SECRET", ""))
    ap.add_argument("--input", default=DATA)
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    with open(args.input, encoding="utf-8") as f:
        doc = json.load(f)

    # 1. 生成 HTML（无论有无凭证都先生成, 降级路径保底）
    html_content = build_article_html(doc, no_figures=args.no_figures)
    date_str = doc.get("date", datetime.date.today().isoformat())
    title = f"每日论文精选 · {date_str}"
    html_path = os.path.join(OUT, f"article-{date_str}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[1/3] 公众号 HTML 已生成: {html_path} ({len(doc.get('papers', []))} 篇, {'纯文本' if args.no_figures else '含图位'})")

    # 2. 凭证检查
    if args.html_only or not (args.appid and args.secret):
        print("[2/3] 未提供 WECHAT_APPID/WECHAT_SECRET -> 降级为粘贴模式")
        print("[3/3] 请打开 HTML 全选复制, 粘贴进公众号编辑器手动发布")
        return

    # 3. 鉴权
    try:
        token = get_token(args.appid, args.secret)
        print("[2/3] access_token 获取成功")
    except RuntimeError as e:
        print(f"[!] {e}")
        print("[3/3] 已降级为粘贴模式(HTML已生成), 排查后可重试")
        return

    if args.dry_run:
        print("[3/3] dry-run 到此为止(未写草稿)。凭证有效, 补 --thumb-media-id 即可真实入库")
        return

    # 4. 写草稿箱（需要封面）
    if not args.thumb_media_id:
        print("[!] 缺少 --thumb-media-id: draft/add 强制要封面。")
        print("    请在公众号后台素材库上传品牌封面图, 复制其 media_id 后重跑(或设 WECHAT_THUMB_MEDIA_ID 环境变量)")
        print("    HTML 粘贴版已生成可先用。")
        return
    try:
        media_id = add_draft(token, title, html_content, args.thumb_media_id,
                             digest=f"三维重建×World Model · {len(doc.get('papers', []))} 篇精选")
        print(f"[3/3] 草稿已入草稿箱 media_id={media_id} -> 请到公众号后台手动点群发(约10秒)")
    except RuntimeError as e:
        print(f"[!] 草稿创建失败: {e}")
        print("    HTML 粘贴版已生成可先用。")


if __name__ == "__main__":
    main()
