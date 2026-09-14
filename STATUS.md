# Paper Daily · 运行状态

**最后更新：2026-09-14**

| 项 | 状态 |
|---|---|
| 每日更新 | ⏸️ 定时任务存在但为 PAUSED（每日 08:00 北京时间；说「恢复更新」即可激活） |
| 研究方向 | **稀疏视角下的 4DGS 新视角合成**（2026-09-14 按论文库重校准） |
| 检索源 | 不设限制、只做审核打分：HF Daily + AI HOT 中文策展池 + 公众号（宽检索）+ arXiv 兜底 |
| 自定义域名 | yilinsforest.me（DNS：dns27/dns28.hichina.com，GitHub Pages 托管）✅ 已生效 |
| 当前期号 | No.253（2026-09-10） |
| 网页视图 | 双视图：**概览（仪表盘）** + 精读（翻卡），默认进概览 |

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

## 网页视图（v1.2，2026-09-14）

移植「AI 晨报仪表盘」的信息架构，保留原有抹茶绿杂志感配色。默认进入**概览视图**：

- **Hero**：kicker + 期号 + 人话日期（`2026年9月10日 星期四`）+ 四枚统计胶囊（总数 + 三档分布）+ 导语条
- **锚点导航**：三档分层，吸顶、滚动高亮（IntersectionObserver），带计数与色点
- **卡片网格**：`auto-fill minmax(320px, 1fr)`；卡片含序号徽标、分类 chip、中文标题、≤60 字摘要、
  元信息行（高校 / star / 被引 / 评分，为空则整行省略）、「精读」+「原文」+「代码」操作
- **文末**：总篇数 + 数据源署名

**三档分层**（`frontend/src/utils/groups.ts`，按关键词判定，非人工标注）：

| 层次 | 判据 | 色 |
|---|---|---|
| 核心方向 CORE | 稀疏视角 NVS / 4DGS / 高斯泼溅 / 前馈几何（VGGT·DUSt3R）/ NeRF | 深抹茶 |
| 相关方向 RELATED | 世界模型 / 视频扩散 / 单目几何 / 点云 / 3D 感知 | 中抹茶 |
| 邻近领域 NEARBY | 其余可借鉴领域 | 灰绿 |

编号**全局连续**（跨档累加不重置），与晨报口径一致。

其他交互：`G` 切视图、`Esc` 从精读返回概览、`T` 主题、`C` 复制、`?` 帮助；
深链 `#read/<n>` 直达第 n 篇精读、`?theme=dark|light` 指定主题（均可分享）。

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
- 本机 `http_proxy` 常指向失效端口，脚本已内置直连 opener；git 推送前需 `unset http_proxy https_proxy`，
  并加 `-c http.proxy= -c https.proxy=`，否则推送会静默失败。
- 公众号源依赖 `scripts/wechat_search/`（node + cheerio，仓库内自包含）。
- **受管 Node 版本会升级**（`22.22.2-2` → `22.22.2-3` 已发生），硬编码路径会让公众号源静默失败。
  `sources_wechat.py` 的 `_find_node()` 已改为自动扫描受管目录取最新版本；新增脚本请沿用同样做法。
- 前端产物 `web/assets/` 的文件名带内容哈希，部署时须**先删旧目录再复制**，避免残留旧 bundle。
- 本地快速验证网页：`chrome --headless=new --screenshot=<绝对路径> "file:///.../web/index.html?theme=dark#read/2"`
  （截图输出路径必须写绝对路径，相对路径会被拒绝访问）。
