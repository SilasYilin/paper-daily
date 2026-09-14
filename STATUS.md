# Paper Daily · 运行状态

**最后更新：2026-09-14**

| 项 | 状态 |
|---|---|
| 每日更新 | ⏸️ 定时任务存在但为 PAUSED（每日 08:00 北京时间；说「恢复更新」即可激活） |
| 研究方向 | **稀疏视角下的 4DGS 新视角合成**（2026-09-14 按论文库重校准） |
| 检索源 | 不设限制、只做审核打分：HF Daily + AI HOT 中文策展池 + 公众号（宽检索）+ arXiv 兜底 |
| 自定义域名 | yilinsforest.me（DNS：dns27/dns28.hichina.com，GitHub Pages 托管） |
| 当前期号 | No.246（2026-09-03） |

## 研究方向画像（v1，2026-09-14）

依据 `C:/Users/25432/Desktop/paper` 下 57 篇论文（`look/` 待读、`star/` 重点）校准，
主线：**稀疏视角 4DGS 的新视角合成**。

| 轴 | 权重 | 代表工作 |
|---|---|---|
| Sparse-view NVS | 1.00 | AnySplat、MV-DUSt3R+、GLADOS、SEVA、UniWorld-View |
| 4DGS / Dynamic GS | 0.98 | 4DGS、Deformable/Dynamic 3D Gaussians、Shape of Motion、Vista4D、NeoVerse |
| Feed-forward 3D Geometry | 0.90 | DUSt3R/MASt3R/Cut3R/Fast3R、VGGT 系、Pi3、TTT3R、DA3、MegaSaM |
| Video Diffusion / World Model | 0.78 | Wan2.1、Cosmos、FlashWorld、FantasyWorld、PixWorld、Lyra |
| Monocular Geometry & Depth | 0.72 | Depth Anything 3、PointDiT、InfiniDepth |
| 3D Perception & VFM | 0.62 | SAM 3、DINOv3、3D+LLM |
| Point Cloud Backbones | 0.55 | PointNet++、Point Transformer V3 |
| 3D Vision Adjacent | 0.45 | 邻接领域（保召回，排序自然靠后） |

## 检索口径变更（v1）

- **解除来源限制**：不再限定公众号与定向组合词，改为按方向宽检索；硬排除仅保留医学/临床等完全无关领域（原 robot / lidar / 自动驾驶 / 遥感 / 硬件等已全部放行）。
- **只做审核**：靠偏好画像打分排序决定去留，而非入池前拦截。
- arXiv 分类新增 `cs.GR`（图形学，渲染 / 新视角合成相关）。
- 关键词清理：移除 `nvs` / `dit` / `seg` / `dino` / `clip` / `generalizable` 等易误命中的短泛词；
  裸词 `world model` 只保留在低权邻接轴，避免智能体 / RL 世界模型抢占主线。

## 恢复/暂停更新

- 暂停：WorkBuddy 对话中说「暂停 paper-daily 更新」，并把定时任务置 PAUSED
- 恢复：说「恢复更新」，把定时任务置 ACTIVE

## 每日管道

1. `scripts/run_daily.py --dry-run --no-figures`（HF / AIHOT / 公众号 / arXiv → 打分筛选 → 写入 `data/today.json`）
2. 智能体精读：写入 `data/llm_summaries.json` → `scripts/merge_llm.py` 合并
3. `scripts/build_web_data.py` 生成 `web/data.js`（axes 用「稀疏视角 4DGS · 新视角合成」）
4. `cd frontend && npm run build` → 拷贝 `frontend/dist/*` 到 `web/`
5. `git add -A && git commit && git push origin main`（推送前先 unset 代理变量）

## 已知问题与注意

- **arXiv 接口在 2026-09-14 本机不可达**（SSL UNEXPECTED_EOF，重试 3 次均失败）。
  已修复连带问题：HF 载荷自带 title/summary，现已持久化为候选兜底，arXiv 不可达时仍能打分（此前会 0 命中）。
  arXiv 恢复前候选池仅 HF 约 50 篇，精选质量受限。
- `web/CNAME` = yilinsforest.me，勿删。
- 本机 `http_proxy` 常指向失效端口，脚本已内置直连 opener；git 推送前需 `unset http_proxy https_proxy`。
- 公众号源依赖 `scripts/wechat_search/`（node + cheerio，仓库内自包含）。
