# 每日论文检索 · 信息源调研清单（初稿 v1）

> 调研日期：2026-08-27 · 状态：待用户审阅
> 用户方向：三维重建（3D Reconstruction）/ World Model（世界模型）

## 可达性验证结果（本机实测）

| 信息源 | 状态 | 验证方式 | 说明 |
|---|---|---|---|
| arXiv RSS (cs.CV/cs.AI/cs.LG/cs.RO) | ✅ 可用 | export.arxiv.org/rss/cs.CV 返回 200 | 每日新论文全量列表，含摘要，跳过周末 |
| arXiv API（关键词检索） | ✅ 可用 | export.arxiv.org/api/query 返回 200 | 按关键词/类别检索，支持全文摘要 |
| GitHub API（star 数/仓库检索） | ✅ 可用 | api.github.com 检索正常 | 获取 star 数、验证论文官方仓库 |
| HuggingFace Papers | ⚠️ 直连超时 | curl 超时，hf-mirror.com 页面 200 | 需走 hf-mirror.com 镜像抓取，或申请 token |
| Semantic Scholar API | ⚠️ 限流 429 | 公共额度被限 | 可用（被引次数数据源），需退避重试或申请免费 API key |
| OpenReview API | ⚠️ 有浏览器验证 | 返回验证页 | 需浏览器自动化访问，列为备选 |

---

## 一、核心学术源（机器可抓取，作为主数据源）

### 1. arXiv 每日新论文（主力源）⭐⭐⭐⭐⭐
- **用途**：每日 cs.CV / cs.AI / cs.LG / cs.RO 新论文全量列表
- **方式**：RSS + API，带完整摘要、作者、类别
- **筛选**：按关键词过滤（3D reconstruction, Gaussian Splatting, NeRF, world model, novel view synthesis, 3D scene understanding, video generation, embodied 等）+ LLM 相关性打分
- **成本**：免费、稳定、无登录

### 2. HuggingFace Daily Papers（质量信号源）⭐⭐⭐⭐⭐
- **用途**：社区 upvote 排名的每日热门论文（天然的质量预筛，与本方向高度重合）
- **方式**：经 hf-mirror.com 镜像抓取
- **价值**：upvote 数可作为「新论文热度」指标，弥补新论文没有引用数的空窗

### 3. Papers with Code / GitHub（影响力验证源）⭐⭐⭐⭐
- **用途**：旧论文的被引/Star 验证、开源代码链接
- **方式**：GitHub API（已验证可用）+ Semantic Scholar（限流需处理）

### 4. Semantic Scholar（被引次数源）⭐⭐⭐⭐
- **用途**：旧论文（2025 年前）被引次数查询
- **方式**：API 可用但公共额度限流，建议申请免费 API key，或用退避策略（每分钟 <30 次够用）

### 5. OpenReview（顶会源，备选）⭐⭐⭐
- **用途**：CVPR/ICCV/NeurIPS/ICLR 投稿与录用论文、评审意见
- **方式**：有浏览器验证，需自动化，第二阶段接入

---

## 二、中文媒体源（公众号类，辅助发现 + 中文解读）

> 公众号无开放 API，抓取均需间接手段，列为**辅助源**，第二阶段逐步接入。

| 公众号 | 定位 | 与方向相关度 | 接入方式（候选） |
|---|---|---|---|
| 机器之心 | AI 学术前沿综合 | 高（常发 3D/生成方向论文解读） | 官网 jiqizhixin.com 有公开文章页可抓 |
| 量子位 | AI 资讯综合 | 中高 | 官网 qbitai.com 可抓 |
| 新智元 | AI 资讯综合 | 中 | 官网/第三方聚合 |
| 我爱计算机视觉 | CV 方向垂直 | 极高（本方向垂直号） | 公众号为主，需搜狗微信/间接抓取 |
| 3D视觉工坊 | 3D 视觉垂直 | 极高（本方向垂直号） | 同上 |

- **共性策略**：公众号本身难直接抓 → 优先抓其**官网/网站版**（机器之心、量子位有站），垂直号（我爱计算机视觉、3D视觉工坊）走搜狗微信搜索或浏览器自动化，试运行期验证稳定性。

---

## 三、社媒/视频源（论文讲解与热度信号，辅助源）

| 平台 | 价值 | 可行性 | 接入方式 |
|---|---|---|---|
| B站 | 论文讲解视频多（中文讲解 3DGS/世界模型的工作很多） | 高 | opencli 支持 bilibili，可搜标题关键词 |
| YouTube | 英文 paper review / demo 视频 | 高 | opencli 支持 youtube |
| 知乎 | 论文解读专栏、专业讨论 | 中高 | opencli 支持 zhihu |
| 小红书 | 逐渐有科研博主发论文速览，前瞻性弱一些 | 中 | opencli 支持 xiaohongshu（可能需登录态，试运行期验证） |
| 抖音 | 科普向居多，学术密度低 | 低 | opencli 支持 douyin，优先级最低 |

**用法定位**：视频/社媒不作为论文发现主源，而是作为「热度信号 + 讲解链接」——当某篇论文在 B站/YouTube 已有讲解视频时，在展示页附上讲解链接，方便快速理解。

---

## 四、信息源分层策略（建议）

```
第一层（每日必抓，机器可稳定抓取）
 ├─ arXiv RSS/API        → 新论文全量池（关键词 + LLM 相关性打分）
 ├─ HF Daily Papers      → 社区热度信号（upvote）
 └─ GitHub API           → star 数、代码仓库验证

第二层（每日尝试，失败不阻塞）
 ├─ 机器之心/量子位官网   → 中文解读发现
 └─ Semantic Scholar     → 被引数（旧论文）

第三层（增强，第二阶段接入）
 ├─ 垂直公众号（我爱计算机视觉、3D视觉工坊）
 ├─ B站/YouTube 讲解视频链接
 └─ OpenReview 顶会数据
```

## 五、论文筛选规则（初稿，待你审阅迭代）

**旧论文（2025 年前）**：
- 被引次数 ≥ 15 或 GitHub star ≥ 100 -> 入选候选（2026-08-27 用户放宽）
- 顶会（CVPR/ICCV/ECCV/NeurIPS/ICLR/SIGGRAPH） oral/spotlight 优先
- 经典奠基工作（如 3DGS 原论文）单独标记「经典」标签

**新论文（2025 年及以后）**：
- 作者影响力：已知知名机构/学者（如 INRIA、DeepMind、OpenAI、字节、清华等）加分
- HF upvote ≥ 30 加分；有关联 GitHub 仓库加分
- LLM 相关性打分（针对三维重建/世界模型方向）≥ 阈值才入选

**你的偏好反馈闭环（核心）**：
- 每日展示后你标注「喜欢/不喜欢 + 原因」
- 我维护一份偏好画像文件，逐周迭代筛选关键词与权重
