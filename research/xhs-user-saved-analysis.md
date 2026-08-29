# 用户小红书收藏·科研风格与信号分析（2026-08-29 抓取）

## 用户收藏的科研帖（7 篇技术向，出自 opencli xiaohongshu saved）
| 帖子 | 作者 | 点赞 | 关键信号 |
|---|---|---|---|
| 面向导航仿真的世界模型技术导论 | 彭思达 | 198 | 教程型：CCF-CV 讲习班、三维世界模型（标定/点云/高斯）+视频世界模型体系化综述，附 Tutorial PDF |
| 把全景图直接生成能漫游的3D房间（Pano2World） | 🦀博士侃AI | 21 | 语言风格标杆（用户指定参考） |
| 港科大&阿里 Glob3R：3D重建别只靠一遍前向 | AI先声 | 33 | **长序列/大场景重建一致性**（Pi3X+密集匹配+滑窗 BA）——正是用户研究方向 |
| GPT 也能够直接生成3D世界了（GaussianGPT, ECCV26） | AI蜘蛛侠 | 288 | 自回归 Transformer 生成 3D 高斯场景（token 化+逐点预测） |
| 聊一聊2026年3D基础模型方向有啥能做的 | 彭思达 | 669 | **Implicit Decoder 机会**（CLAY/D4RT/InfiniDepth；显存/任意点索引）——用户关注的前沿讨论 |
| 论文写作导览图 | - | - | 写作辅助 |
| （另：R2M-Bench 在公众号也有讨论，见 media_mentions） | | | |

## 风格结论（用于 LLM prompt 校准）
1. 用户收藏密度最高的是**彭思达**（浙大 3D 视觉学者）的体系化内容 + 博士侃AI 的通俗讲解——「专业底子+人话表达」双轨都要。
2. 讲法结构：痛点场景 → 方法核心一句话比喻（「前向模型=快速草图，Glob3R=找对应关系再校准」）→ 机制拆解 → 结果数字（PSNR/速度对比）→ 诚实边界。
3. 关注主题信号（可加入偏好画像关键词）：
   - `长序列重建一致性 / 尺度漂移 / 轨迹漂移`（Glob3R、VGGT-Align）
   - `3D 基础模型 / implicit decoder / scaling`（彭思达帖）
   - `自回归 3D 生成 / GaussianGPT`（AI蜘蛛侠帖）
   - `导航仿真 × 世界模型`（彭思达 Tutorial）
4. 点赞数 ≠ 偏好（用户收藏了 21 赞的博士侃AI），「收藏行为本身」才是最强偏好信号。

## 可执行动作
- [x] 把上述关键词补进 config/preference-profile.json 关键词表（frontier axes）
- [x] media_monitor 查询词加「3D基础模型」「GaussianGPT」「Glob3R」类
- [x] 风格规范并入 research/xhs-style-reference.md
