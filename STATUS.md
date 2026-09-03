# Paper Daily · 运行状态

**最后更新：2026-09-03**

| 项 | 状态 |
|---|---|
| 每日更新 | ✅ 已恢复（WorkBuddy 定时自动化，每日 08:00 北京时间） |
| 检索源 | HF Daily 主源 + **AI HOT 中文策展池** + **公众号（wechat-article-search skill 通道）** + arXiv 兜底 |
| 自定义域名 | yilinsforest.me（DNS：dns27/dns28.hichina.com，GitHub Pages 托管） |
| 当前期号 | No.246（2026-09-03） |

## 恢复/暂停更新

- 暂停：WorkBuddy 对话中说「暂停 paper-daily 更新」并将定时任务置 PAUSED
- 恢复：说「恢复更新」并重新激活定时任务

## 每日管道（v1.0，2026-09-03 重构）

1. `scripts/run_daily.py --dry-run`（抓取 HF/AIHOT/公众号/arXiv → 筛选 → 兜底总结）
2. 智能体精读：把总结写入 `data/llm_summaries.json` → `scripts/merge_llm.py` 合并
3. `scripts/build_web_data.py` 生成 `web/data.js`
4. `cd frontend && npm run build` → 拷贝 `frontend/dist/*` 到 `web/`
5. git commit + push（触发 GitHub Pages 部署）

## 注意

- `web/CNAME` = yilinsforest.me，勿删
- 本机代理变量失效时脚本已内置直连 opener
- 公众号源依赖 `scripts/wechat_search/`（node + cheerio，仓库内自包含）
