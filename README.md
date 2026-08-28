# Paper Daily · 每日论文精选

面向「三维重建（3D Reconstruction）× 世界模型（World Model）」方向的个人每日论文精选系统。

## 架构

```
每日 08:00 (cron)
  └─ run_daily.py
       ① arXiv API 抓取（cs.CV / cs.AI / cs.LG / cs.RO，默认 150 条）
       ② 偏好画像双轨硬过滤 + 相关度打分排序（config/preference-profile.json）
       ③ LLM 中文导读 + 0-6 结构化字段（agent_plan glm-5.3 / DeepSeek / 保守兜底三级）
       ④ data/today.json -> build_web_data.py -> web/data.js
       ⑤ 静态网页 web/index.html 自动渲染（无需重启）
```

## 本地使用

```bash
# 手动跑一次（先 dry-run 验证）
python3 scripts/run_daily.py --dry-run --categories cs.CV --max 8

# 全流程（含网页数据生成）
python3 scripts/run_daily.py --categories cs.CV,cs.AI --max 8

# 直接打开网页
open web/index.html   # 或双击，单文件离线可开
```

## LLM 配置（可选，三级自动降级）

| 优先级 | 方式 | 配置 |
|---|---|---|
| 1 | agent_plan（火山方舟订阅） | 环境变量 `AGENT_PLAN_API_KEY`（或自动读 OpenClaw 平台配置） |
| 2 | DeepSeek | 环境变量 `DEEPSEEK_API_KEY` |
| 3 | 保守兜底 | 无需配置，宁留白不编造 |

## 目录

```
config/   偏好画像（feedback_log 只追加）
data/     每日精选产出（today.json）
scripts/  管道脚本（run_daily / build_web_data）
spec/     论文总结模板（0-6 字段契约）
web/      静态网页（index.html + data.js，可托管 GitHub Pages / Vercel）
research/ 前期调研（信息源 / 网页模板）
demo/     方案演示页（A/B/C 三选一定稿 B）
```

## 红线

- 论文总结不编造数字，未确认处写「以原文为准」
- `figure_url` 默认 `null`（简洁无图偏好）
- `feedback_log` 只追加不覆盖
