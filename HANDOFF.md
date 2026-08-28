# 项目交接文档：「每日论文精选」系统

> 交接日期：2026-08-27 · 交接原因：用户转接给新 agent
> 项目目录：/root/.openclaw/workspace/paper-daily/

---

## 一、项目背景与目标

用户是**人工智能方向研究生**，研究方向：**三维重建（3D Reconstruction）+ World Model（世界模型）**。

目标：搭建一套**每日论文检索 → 筛选 → 总结 → 网页展示**的自动化系统：
1. 每天自动从多信息源检索方向相关新论文
2. 按筛选规则（新旧论文双轨制）过滤 + LLM 相关性打分
3. 每篇论文按用户模板生成专业总结，含从论文 PDF 截取的流程图
4. 展示到一个已选定风格的网页（**方案 B：杂志感**），每日更新
5. 用户每日审阅并反馈喜欢/不喜欢+原因 → 偏好画像持续迭代

## 二、用户已确认的决策（不要推翻，除非用户主动提出）

| 决策项 | 结论 |
|---|---|
| 信息源分层 | 三层结构（见下），一期跑通第一层学术源闭环 |
| 筛选规则 | 旧论文（2025 前）：被引 ≥15 或 star ≥100 入选；顶会 oral/spotlight 优先；新论文（2025 后）：知名机构作者 + HF upvote ≥30 + 有代码仓库加分 |
| 网页方案 | **方案 B（option-b.html，alphaXiv 杂志感风格）**：大图 + AI 一句话总结，视觉冲击力优先 |
| 论文总结模板 | 已固化，见 spec/paper-summary-template.md，字段 0-6（Background/Task/Insight/Pipeline/Methods/Experiment/Limitation），回答需专业正确；用户提问时须提及涉及论文哪一部分；「笔记版本」仅用户明确要求时启用（LaTeX 不渲染、不分行、代码表示变量、模块分割线、无多余符号） |

## 三、信息源架构（已实测验证）

**第一层·每日必抓（机器稳定可抓）**
- arXiv RSS：export.arxiv.org/rss/cs.CV（✅ 实测 200，含完整摘要，跳过周末）；类别建议 cs.CV/cs.AI/cs.LG/cs.RO
- arXiv API：export.arxiv.org/api/query（✅ 实测 200）
- GitHub API：api.github.com（✅ 实测 200，star 数/仓库检索）
- HF Daily Papers：**huggingface.co 直连超时，必须走 hf-mirror.com 镜像**（✅ 页面 200；注意 /api/daily-papers 在镜像上返回 401，需抓页面解析）

**第二层·尽力抓取（失败不阻塞）**
- 机器之心 jiqizhixin.com、量子位 qbitai.com（官网文章页）
- Semantic Scholar API（⚠️ 公共额度限流 429，需退避重试，建议申请免费 API key；用途：被引次数）

**第三层·二期增强**
- 垂直公众号：我爱计算机视觉、3D视觉工坊（无 API，需搜狗微信/浏览器自动化）
- B站/YouTube 论文讲解视频（opencli 支持 bilibili/youtube；定位是「热度信号+讲解链接」，不作论文发现主源）
- 小红书（opencli 支持，可能需登录态）、抖音（优先级最低）、X
- OpenReview API（⚠️ 有浏览器验证，需自动化）

## 四、关键文件清单

| 文件 | 内容 |
|---|---|
| paper-daily/spec/paper-summary-template.md | 论文总结模板（用户确认版）+ 筛选规则 v1 |
| paper-daily/research/sources-survey.md | 信息源调研清单（含可达性实测） |
| paper-daily/research/web-template-survey.md | 8 个网站模板调研报告 |
| paper-daily/demo/option-a.html | 方案 A 演示页（组合方案，未选用，可参考其字段完整性） |
| paper-daily/demo/option-b.html | **方案 B 演示页（已选定，正式版开发基础）** |
| paper-daily/demo/option-c.html | 方案 C 演示页（工具风，未选用） |

## 五、当前进度

- [x] 信息源调研与可达性实测
- [x] 网页模板调研（8 站对比）
- [x] 三方案演示页制作并交付用户挑选
- [x] 用户选定方案 B
- [x] 论文总结模板固化
- [ ] **正式版网页开发**（基于 option-b.html，接入真实数据管道）
- [ ] **每日检索脚本/管道**（arXiv RSS → 关键词+LLM 打分 → 筛选 → 按模板总结 → 抓取论文 PDF 流程图 → 生成页面数据）
- [ ] **部署**（方式未定，见待办）
- [ ] **每日定时任务配置**（cron，含 openclaw-cron-enhance skill 流程）
- [ ] **用户偏好画像**（初始依据：用户本地 C:\Users\25432\Desktop\paper 文件夹，见待办）
- [ ] 二期：公众号/视频源接入

## 六、未决事项（新 agent 需向用户确认）

1. **部署位置**：网页放本工作区（经 ArkClaw 访问）还是用户的外部服务器？用户最初说「部署到服务器上」，但未给出服务器信息。
2. **本地论文文件夹**：用户 Windows 本机 C:\Users\25432\Desktop\paper（我方无法直接访问）。需用户提供代表性论文 PDF（拖进对话），用于提炼偏好画像初始权重。
3. **更新时间与推送方式**：每天几点跑？是否需要消息推送提醒（还是纯网页自更新）？

## 七、注意事项

- 流程图：需从论文 PDF 截取 method figure（可下载 arXiv PDF 后用 pdftoppm/PyMuPDF 提取首页/figure 页），注意版权仅个人研究使用
- HF 镜像抓取注意频控；Semantic Scholar 用退避策略
- 筛选阈值是 v1，用户会通过每日审阅反馈迭代，偏好画像要设计成可累积、可回溯的文件
- 每日总结必须按模板字段，内容要专业正确（宁可保守，不要编造数字）
- 团队配置：HTML 页面类工作可派给子 agent a-mtba6yoi7i82ln（HTML页面生成专家），PPT 给 a-mtba7kqpdref8n，情报类给 a-mtba90iaxgv9yj
- 用户沟通偏好：先结论后展开；信息不足时说明假设
