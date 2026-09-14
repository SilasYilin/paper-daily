# Paper Daily · 运行状态

**最后更新：2026-09-14**

| 项 | 状态 |
|---|---|
| 每日更新 | ✅ 已激活（每日 08:00 北京时间，WorkBuddy 定时任务 `644ae714`） |
| 研究方向 | **稀疏视角下的 4DGS 新视角合成**（2026-09-14 按论文库重校准） |
| 检索口径 | **v2**：来源不设限，**优先知名高校/企业 + CCF-A 类会议 Oral·Highlight·Best Paper**，再按方向画像排序 |
| 候选来源 | HF Daily 主源 + **arXiv RSS**（cs.CV/GR/AI/LG/RO，约 600 篇/日）+ AI HOT 中文策展池 + 公众号宽检索 |
| 自定义域名 | yilinsforest.me（DNS：dns27/dns28.hichina.com，GitHub Pages 托管）✅ 已生效 |
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

## 检索口径（v2，2026-09-14 用户指令）

**优先级 = 来源声望 + 方向匹配**，权重配置在 `config/source-prestige.json`，
评分与匹配逻辑在 `scripts/prestige.py`。

| 信号 | 加分 | 识别方式 |
|---|---|---|
| CCF-A / 公认顶会（CVPR、ICCV、NeurIPS、ICML、ICLR、AAAI、SIGGRAPH、TPAMI…） | +0.20 | arXiv Comments 字段 |
| Oral / Highlight / Spotlight / Best Paper 等荣誉 | +0.14 ~ +0.22 | 同上 |
| 顶级高校或企业研究院（含 Google DeepMind、Meta、NVIDIA、清华、MIT… 约 160 条） | +0.16 | arXiv 全文首页作者脚注 |
| 其他正规高校 / 研究机构 | +0.04 | 同上（标签取原文片段） |
| **合计封顶** | **0.42** | 高于任何单一方向轴，确保「优先」真正生效 |

- **Workshop ≠ 正会**：Comments 含 `workshop` 时标注为「XX Workshop」并整体降半，避免误导。
- 单位获取优先走 arXiv 摘要页脚注；无 HTML 版时退 OpenAlex / Semantic Scholar。
- 其余：解除来源限制（仅保留医学/临床硬排除）；关键词已清理 `nvs`/`dit`/`generalizable` 等易误命中短泛词；
  裸词 `world model` 只留在低权邻接轴。

## 网页视图（v1.3，2026-09-14 精简）

保留「晨报仪表盘」信息架构与抹茶绿配色，按用户反馈**删去非关键小字与小模块**：

- 已删：Hero kicker 小字、导语条（edNote 框）、「（北京时间）」、分组英文名与描述小字、
  卡片「创新 x · 效果 y」评分行、页脚第二行说明、精读页快捷键提示行、顶栏重复元信息。
- **Hero**：期号 + 人话日期 + 统计胶囊（总数 / 核心 / 相关 / 邻近，标签已中文化）
- **锚点导航**：三档分层，吸顶 + 滚动高亮，带计数与色点
- **卡片网格** `auto-fill minmax(320px, 1fr)`：序号徽标、**来源声望 chip**（如「CVPR · Oral」，无则回退方向分类）、
  中文标题、≤60 字摘要、元信息行（机构 / star / 被引）、「精读」+「原文」+「代码」
- **文末**：总篇数 + 数据源署名

其他交互：`G` 切视图、`Esc` 从精读返回概览、`T` 主题、`C` 复制、`?` 帮助；
深链 `#read/<n>` 直达第 n 篇精读、`?theme=dark|light` 指定主题。

## 每日管道

1. `scripts/run_daily.py --dry-run --no-figures --llm-top 8 --max 8`
   （HF + arXiv RSS + AIHOT + 公众号 → 方向打分 → **前 60 篇补全会议/机构并加权** → 写入 `data/today.json`）
2. 智能体精读：写入 `data/llm_summaries.json` → `scripts/merge_llm.py` 合并（零 API 成本）
3. `scripts/build_web_data.py` 生成 `web/data.js`
4. `cd frontend && npm run build` → 拷贝 `frontend/dist/*` 到 `web/`
5. `git add -A && git commit && git push origin main`（推送前先 unset 代理变量）

## 脚本清单（v1.3 新增）

| 脚本 | 作用 |
|---|---|
| `scripts/net.py` | 统一网络层：自动探测本机代理（7890 等），失败回退直连，带重试 |
| `scripts/arxiv_web.py` | 解析 arXiv 摘要页（Comments → 会议/荣誉）与全文页（作者脚注 → 机构），带 14 天缓存 |
| `scripts/prestige.py` | 来源声望评分：顶会 / 荣誉 / 知名机构 → 加权与标签 |
| `scripts/sources_arxiv_rss.py` | arXiv RSS 通道，绕开 API 的 IP 限流，单日约 600 篇候选 |
| `config/source-prestige.json` | 会议名单、荣誉词表、约 160 条顶级高校/企业名单 |

## 恢复/暂停更新

- 暂停：WorkBuddy 对话中说「暂停 paper-daily 更新」，并把定时任务置 PAUSED
- 恢复：说「恢复更新」，把定时任务置 ACTIVE

## 已知问题与注意

- **arXiv API（`/api/query`）对本机出口 IP 长期 429 限流**；摘要页与 RSS 不受影响，故候选主通道走 RSS。
  即使未开梯子，管道也能靠 HF Daily 出刊。
- `web/CNAME` = yilinsforest.me，勿删。
- 本机 `http_proxy` 指向 127.0.0.1:7890（梯子未开时失效）；`net.py` 已自适应处理，
  但 **git 推送仍须** `unset http_proxy https_proxy` 并加 `-c http.proxy= -c https.proxy=`，否则静默失败。
- 公众号源依赖 `scripts/wechat_search/`（node + cheerio，仓库内自包含）。
- **受管 Node 版本会升级**（`22.22.2-2` → `22.22.2-3` 已发生），硬编码路径会让公众号源静默失败。
  `sources_wechat.py` 的 `_find_node()` 已改为自动扫描取最新版本；新增脚本请沿用。
- 前端产物 `web/assets/` 文件名带内容哈希，部署时须**先删旧目录再复制**。
- 本地快速验证：`chrome --headless=new --screenshot=<绝对路径> "file:///.../web/index.html?theme=dark#read/2"`
  （截图路径必须写绝对路径）。
