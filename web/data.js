window.PAPER_DAILY_DATA = {
  "issue": "No.240",
  "date": "2026-08-28",
  "axes": "三维重建 × 世界模型",
  "edNote": "本期精选基于偏好画像筛选与排序。",
  "hero": {
    "title": "Thinking on Shots: Consistent Multi-Shot Video Editing with Agentic Reasoning",
    "authors": "Chenyang Wu et al.",
    "venue": "arXiv 2026.08 · Project Page: https://wucy0519.github.io/MMLVE/ and see sour",
    "summary": "现有生成式AI视频编辑方法主要聚焦单镜头或短视频片段，长视频多指令编辑仍是难题：朴素的固定时长分块策略容易导致实体碎片化、严重编辑幻觉和时间连续性被破坏。本文提出多指令多镜头长视频编辑任务（MMLVE），围绕跨镜头编辑一致性（CSEC）、多指令解耦（MID）与时空结构零破坏（ZDSS）三大核心目标展开。方法上提出智能体编辑框架 MMLVE-Agent，利用 LLM 与 VLM 的协同实现镜头级视频解耦与精准指令解析。同时构建了面向 MMLVE 的基准数据集 MMLVE-Bench 及三项专用评测指标。实验表明该方法优于 Seedance 2.0 等闭源 SOTA 方案，能消除编辑幻觉、保持跨镜头一致并实现无缝时空过渡（具体数值以原文为准）。",
    "paperUrl": "https://arxiv.org/abs/2608.26809",
    "score": 0.59,
    "category": "AGENTIC VIDEO EDITING × LLM/VLM 智能体",
    "influence": "待补充",
    "figure": {
      "url": null,
      "caption": ""
    },
    "fields": {
      "background": "生成式AI显著推进了视频编辑，但现有方法主要面向单镜头或短片段；长视频多指令编辑中，朴素分块策略（如固定时长切分）会导致实体碎片化、严重编辑幻觉和时间连续性中断。",
      "task": "提出多指令多镜头长视频编辑（MMLVE）任务，包含三大核心目标：跨镜头编辑一致性（CSEC）、多指令解耦（MID）、时空结构零破坏（ZDSS）。",
      "insight": "将长视频编辑转化为镜头级解耦与指令解析问题：通过 LLM 与 VLM 的智能体协同推理在镜头粒度上理解视频结构与指令，从而替代固定时长切块并保障跨镜头一致性与时序连续性。",
      "pipeline": "智能体编辑框架：利用 LLM 与 VLM 协同完成镜头级视频解耦与精准指令解析，进而执行一致的多镜头编辑（具体流程细节以原文为准）。",
      "methods": "基于 LLM 与 VLM 协同的智能体编辑框架（MMLVE-Agent）；具体模型模块与算法设计以原文为准。",
      "experiment": "构建 MMLVE-Bench 数据集（具备复杂真实时空动态、高密度异构指令、稀疏随机实体分布）并提出三项 MMLVE 专用评测指标；大量实验显示 MMLVE-Agent 优于 Seedance 2.0 等闭源 SOTA，消除编辑幻觉、保持跨镜头编辑一致并实现无缝时空过渡（具体数据以原文为准）。",
      "limitation": "以原文为准"
    }
  },
  "papers": [
    {
      "title": "SpatialCrafter: Single Image World Modeling with Generative 3D Proxies",
      "authors": "Chuan Fang et al.",
      "venue": "arXiv 2026.08 · 12 pages",
      "summary": "SpatialCrafter 面向单张图像生成可探索场景的任务，指出基于视频扩散模型（VDM）的现有方法依赖稀疏点云或二维全景等不完整条件信号，易产生随机幻觉、长期漂移和欠佳的三维一致性。其提出两阶段框架：先用 PaSS Flow 模块预测空间对齐、几何一致的全局三维代理，再将 VDM 重构为生成式延迟精修器（Generative Deferred Refiner），在代理定义的场景几何上合成高频真实感细节。为与预训练 VDM 兼容，引入 Parallel Geometry Injection 与 Proxy-Aware Corruption 两种训练策略，在不破坏预训练生成流形的前提下提升对代理伪影的鲁棒性。作者还构建了首个面向图像到场景生成的混合大规模数据集（场景规模以原文为准）。实验表明该方法在合成与真实数据上优于 SOTA，缓解长期漂移，并在快速相机运动与极端视角变化下保持稳健一致。",
      "paperUrl": "https://arxiv.org/abs/2608.27073",
      "score": 0.5,
      "category": "IMAGE-TO-SCENE 世界模型 × 生成式3D代理",
      "influence": "待补充",
      "figure": {
        "url": null,
        "caption": ""
      },
      "fields": {
        "background": "可探索的图像到场景生成对游戏、机器人与虚拟现实等应用至关重要；现有基于视频扩散模型（VDM）的方法普遍依赖稀疏点云或二维全景等不完整条件信号，导致随机幻觉、长期漂移与欠佳的三维一致性。",
        "task": "单张图像驱动的可探索场景生成（image-to-scene 世界建模），需在高保真外观的同时保证三维几何一致性，并支持快速相机运动与极端视角变化下的场景漫游。",
        "insight": "将生成过程解耦为'全局三维代理生成 + 外观精修'两阶段：以空间对齐、几何一致的全局 3D 代理为扩散生成提供强几何锚定，从源头抑制幻觉与长期漂移；并以不破坏预训练生成流形的方式向 VDM 注入几何信息。",
        "pipeline": "两阶段流程：第一阶段由 Point-anchored Sparse Structure (PaSS) Flow 模块从单图预测空间对齐、几何一致的全局三维代理；第二阶段将预训练 VDM 重构为 Generative Deferred Refiner，在代理定义的场景几何之上合成高频真实感细节；训练侧配合 Parallel Geometry Injection 与 Proxy-Aware Corruption 策略以增强对代理伪影的鲁棒性。",
        "methods": "PaSS Flow（点锚定稀疏结构流模块）、Generative Deferred Refiner（生成式延迟精 refin 阶段）、Parallel Geometry Injection 与 Proxy-Aware Corruption 训练策略；另构建首个面向图像到场景生成的混合大规模数据集（规模以原文为准）。",
        "experiment": "在合成与真实世界数据集上开展大量实验，结果显示其优于 SOTA 方法，缓解了长期漂移，并在快速相机运动与极端视角变化下保持鲁棒与一致；代码、模型与新构建数据集将公开发布。",
        "limitation": "以原文为准"
      }
    },
    {
      "title": "CLAP: Cross-Embodiment Video World Models are Zero-Shot Physical Simulators",
      "authors": "Kechen Liu et al.",
      "venue": "arXiv 2026.08",
      "summary": "现有动作条件视频模型大多局限于单一机器人本体，无法利用互联网规模异构视频中蕴含的丰富物理信号。CLAP 提出跨本体动作条件视频生成框架，基于“普适物理定律支配时空动态而与执行者无关”的洞察，用末端执行器位姿、语言指令与潜在动作统一异构动作空间。其课程式训练先用潜在动作在无标注视频上学习物理先验，再接地到末端执行器动作空间以实现零样本真实任务部署。在 DROID 等挑战性环境中，CLAP 接近或超越单本体 SOTA 视频模型，并通过少样本适应确立训练单本体视频世界模型的新范式，覆盖跨本体、DROID、Bridge、双臂 YAM 与 G1 人形等多种设置；代码与模型全部开源。",
      "paperUrl": "https://arxiv.org/abs/2608.27406",
      "score": 0.48,
      "category": "VIDEO WORLD MODEL × CROSS-EMBODIMENT",
      "influence": "待补充",
      "figure": {
        "url": null,
        "caption": ""
      },
      "fields": {
        "background": "最先进的动作条件视频模型通常局限于单一机器人本体，难以利用互联网规模的异构视频（含人类与机器人智能体）中利于学习可泛化物理的信号；且跨机器人平台动作表示差异极大、人类视频普遍缺少动作标注。",
        "task": "跨本体动作条件视频生成，作为零样本物理模拟器/视频世界模型，并零样本部署到真实世界任务。",
        "insight": "普适物理定律支配时空动态而与执行者无关，因此可在异构本体数据上学习统一物理先验，再接地到具体动作空间以部署。",
        "pipeline": "课程式两阶段：先在无标注视频数据上用潜在动作学习基础物理先验，随后在末端执行器动作空间中接地，实现零样本真实任务部署，并可经少样本适应进一步提升。",
        "methods": "用末端执行器位姿、语言指令与潜在动作三类表示统一异构动作空间，并结合课程式跨本体学习配方；具体网络结构与训练细节以原文为准。",
        "experiment": "在 DROID、Bridge、双臂 YAM、G1 人形及跨本体等多种动作空间与机器人形态上评估，接近或超越单本体 SOTA 视频模型，少样本适应带来额外增益；具体指标数字以原文为准。",
        "limitation": "以原文为准"
      }
    },
    {
      "title": "R2M-Bench: Evaluating Revisit Memory via Relative Consistency in Interactive Video World Models",
      "authors": "Qiwen Gu et al.",
      "venue": "arXiv 2026.08 · Code: https://github.com/AMAP-ML/R2MBench",
      "summary": "该工作针对交互式视频世界模型中“重访记忆”评测的歧义：首访与重访帧高度相似未必说明模型记住了场景，可能只是中间 rollout 几乎没有变化，使绝对重访分数易受渲染稳定性、重复内容和运动失败的干扰。为此提出 R2M-Bench，为每个检测到的返回在相同 rollout 内构造两个对照——间隔匹配的非重访对（度量一般时间稳定性）与短程对（估计短程一致性），并定义 MemoryGain 与 Normalized Memory Ratio 来衡量超出一般时间稳定性的重访优势。基准由参考场景与离开-返回轨迹组合构成若干实例（具体数量以原文为准），从外观保真、场景与物体身份、局部几何及持久状态等维度评测。在多个动作条件视频世界模型上，Overall NMR 与人类一致性判断呈正相关（相关系数以原文为准），且相比原始重访相似度显著降低与生成运动的相关性、削弱“慢运动捷径”；DreamX-World-Memo 在被评测模型中取得最高 Overall NMR。",
      "paperUrl": "https://arxiv.org/abs/2608.27328",
      "score": 0.48,
      "category": "VIDEO WORLD MODEL × 记忆一致性评测基准",
      "influence": "待补充",
      "figure": {
        "url": null,
        "caption": ""
      },
      "fields": {
        "background": "交互式视频世界模型需要在离开并返回先前场景时维持记忆与一致性，但绝对重访相似度分数易受渲染稳定性、重复内容和运动失败（如慢运动）等混杂因素影响，难以真实反映模型是否记住了场景。",
        "task": "构建评测基准，量化动作条件视频世界模型的“重访记忆”能力，将重访特异的一致性与一般时间稳定性区分开来。",
        "insight": "首访-重访帧相似度高不等于模型记住了场景，可能只是 rollout 变化极小；利用同一 rollout 内的对照对做相对校准，可以剥离一般时间稳定性并抑制慢运动捷径。",
        "pipeline": "对每次检测到的返回，在同一次 rollout 中选取两个对照：间隔匹配的非重visit对（度量一般时间稳定性）与短程对（估计短程一致性），据此计算 MemoryGain（相对时间基线的重访优势）与 Normalized Memory Ratio（以短程-基线动态范围归一化）；基准由参考场景与三条离开-返回轨迹组合构成实例（具体数量以原文为准），评测维度涵盖外观保真、场景与物体身份、局部几何和持久状态。",
        "methods": "相对一致性校准、MemoryGain、Normalized Memory Ratio、重访检测、多维度一致性评测（外观/身份/几何/持久状态）、与人类一致性判断的相关性分析；具体实现细节以原文为准。",
        "experiment": "在多个动作条件视频世界模型上评测（数量以原文为准），Overall NMR 与人类一致性判断呈 Spearman 正相关（数值以原文为准）；NMR 与生成运动的模型内相关幅度显著低于原始重访相似度（数值以原文为准），表明相对校准大幅削弱慢运动捷径；DreamX-World-Memo 获得被评测视频模型中最高的 Overall NMR。",
        "limitation": "以原文为准"
      }
    },
    {
      "title": "Glass Surface Detection Grounded in 3D Visual Geometry",
      "authors": "Yiwei Lu et al.",
      "venue": "arXiv 2026.08 · 9 pages, 10 figures. Accepted by ACM Multimedia 2026",
      "summary": "玻璃表面检测（GSD）对场景理解与重建至关重要，但玻璃的透明性与反光性使其极具挑战，且现有方法多依赖二维外观线索，在几何歧义场景中容易失效。本文提出范式转变：将 GSD 锚定于三维视觉几何，显式建模玻璃的物理存在。方法先从视觉几何基础模型 VGGT 中蒸馏三维先验并生成玻璃感知的三维表征，再通过多任务学习框架与新型玻璃检测头完成检测：其中 FSAM 模块识别玻璃特有的频谱特征用于定位，GeGB 模块将二维特征选择性锚定到三维几何以完成分割。实验表明该方法在多个标准 GSD 基准上达到 SOTA，可泛化到视频/多模态数据，并显著改善含玻璃场景的重建效果（具体数字以原文为准）。",
      "paperUrl": "https://arxiv.org/abs/2608.26752",
      "score": 0.48,
      "category": "GLASS SURFACE DETECTION × 3D VISUAL GEOMETRY",
      "influence": "待补充",
      "figure": {
        "url": null,
        "caption": ""
      },
      "fields": {
        "background": "玻璃因透明与反光特性，其检测对场景理解与重建既关键又困难；现有 GSD 方法主要依赖二维外观线索，在几何歧义场景下容易失效。",
        "task": "玻璃表面检测与分割：以三维视觉几何为基础，实现玻璃表面的定位与分割，并进一步支持视频/多模态输入以及含玻璃场景的三维重建改善。",
        "insight": "提出范式转变：将 GSD 锚定于三维视觉几何以显式建模玻璃的物理存在，而非仅依赖易失效的二维外观线索；同时利用玻璃特有的频谱特征作为检测信号。",
        "pipeline": "先从 VGGT 蒸馏丰富的三维先验并生成玻璃感知的三维表征；随后在多任务学习框架中通过新型玻璃检测头完成检测：FSAM 识别玻璃特异频谱特征用于定位，GeGB 将二维特征选择性锚定于三维几何以完成分割。",
        "methods": "VGGT 三维先验蒸馏、玻璃感知三维表征生成、多任务学习、频率自注意力模块 FSAM（Frequency Self-Attention Module）、几何锚定模块 GeGB（Geometry Grounding Block）。",
        "experiment": "在多个标准 GSD 基准上取得 SOTA 性能（基准数量与指标数值以原文为准），可良好泛化到视频/多模态数据，并显著提升含玻璃场景的重建质量；代码已开源。",
        "limitation": "以原文为准"
      }
    },
    {
      "title": "TADP: Task-Aware Deformable Prediction for Single-Stage 3D Object Detection",
      "authors": "Su Wang et al.",
      "venue": "arXiv 2026.08 · Accepted to the 2023 IEEE Intelligent Vehicles Symposium (IV",
      "summary": "现有单阶段3D目标检测器通常对分类、回归等不同任务复用同一套提取特征，但难以将特征投影到对所有任务都自适应的公共空间。为此本文提出任务感知可变形预测方法TADP：先由三重特征精炼聚合模块自适应提取三级特征，再通过多尺度特征聚合模块以尺度感知方式融合多尺度特征。其核心是即插即用的任务感知可变形预测头，对每个任务的预测施加变形，从而感知各任务的侧重点与相互作用。在KITTI数据集上车类mAP超越众多SOTA方法（具体数值以原文为准），且该变形头迁移到其他检测方法上同样取得良好效果。",
      "paperUrl": "https://arxiv.org/abs/2608.27282",
      "score": 0.44,
      "category": "SINGLE-STAGE 3D DETECTION × TASK-AWARE DEFORMATION",
      "influence": "待补充",
      "figure": {
        "url": null,
        "caption": ""
      },
      "fields": {
        "background": "多数单阶段3D目标检测器对不同任务使用相同提取的特征，而无法将特征投影到对所有任务都自适应的公共空间，导致各任务的需求难以同时满足。",
        "task": "单阶段3D目标检测，并在KITTI基准上验证（含车类检测）。",
        "insight": "不同任务对特征的侧重点与相互交互各不相同，应让每个任务的预测过程具备任务感知能力，通过可变形操作自适应地匹配各任务需求。",
        "pipeline": "首先由三重特征精炼聚合模块自适应提取三级特征；随后用多尺度特征聚合块以尺度感知方式融合多尺度特征；最后通过即插即用的任务感知可变形头对每个任务的预测进行变形。",
        "methods": "三重特征精炼聚合模块、尺度感知的多尺度特征聚合块、即插即用的任务感知可变形预测头，并设计了三种不同的变形模块。",
        "experiment": "在KITTI数据集上车类mAP超越众多SOTA方法（具体数值以原文为准）；可变形头应用于其他检测方法也表现良好，验证了即插即用性与通用性。",
        "limitation": "以原文为准"
      }
    },
    {
      "title": "Anatomy-Guided Foundation Model Adaptation with Within-Case Prototype Supervision for Standard Plane Detection in Fetal Ultrasound Blind Sweeps",
      "authors": "Yuzhe Zhao",
      "venue": "arXiv 2026.08",
      "summary": "该论文针对低成本产科胎儿超声盲扫中的腹围标准切面检测：正帧占比极低、仅形成短连续片段，属于高度不平衡的帧分类问题，现成超声与视觉基础模型难以有效处理。作者提出轻量序列级框架 AnatoProto，在冻结 BiomedCLIP 编码器上通过四个组件完成适配：以 nnU-Net 腹部区域概率为空间先验的解剖加权空间池化、利用同次扫查正帧均值的案例内原型损失、由帧到片段再到案例级拒绝器的三阶段级联精化，以及联合建模帧稳定性与帧间边界转移的混合预测头。在 ACOUSLIC-AI 基准上，AnatoProto 的测试 F1 显著超过最强基础模型基线与最强视频时序动作检测基线（具体数字以原文为准）。协同性研究进一步揭示原型损失与解剖加权池化并非可加关系：单独使用原型损失反而降低召回，二者组合后召回反转为提升，作者将这一符号翻转归因于案例内原型的准确性。",
      "paperUrl": "https://arxiv.org/abs/2608.27051",
      "score": 0.44,
      "category": "FETAL ULTRASOUND × FOUNDATION-MODEL ADAPTATION",
      "influence": "待补充",
      "figure": {
        "url": null,
        "caption": ""
      },
      "fields": {
        "background": "胎儿腹围标准切面检测在低成本产科盲扫中是高度不平衡的帧分类问题：正帧占比不足序列的3%、仅形成短连续片段，现成的超声与视觉基础模型均难以有效处理。",
        "task": "在低资源胎儿超声盲扫序列中检测胎儿腹围（AC）标准切面，即不平衡视频序列上的帧级分类并提升到结构约束的片段级定位。",
        "insight": "冻结基础模型的语义特征需要解剖空间先验引导聚合才能落到有意义区域；帧级监督之外还可利用案例级结构（同一次扫查内正帧的均值原型）。二者存在非可加的协同效应：原型损失单独使用会损害召回，与解剖加权池化组合后反转为提升，根源在于案例内原型的准确性。",
        "pipeline": "冻结 BiomedCLIP 提取 patch token → nnU-Net 输出腹部区域概率作为空间先验，重加权聚合 patch token 得到解剖加权的帧嵌入 → 案例内原型损失将各帧嵌入拉向同扫查正帧均值 → 三阶段级联精化：帧级 → 片段级 → 案例级拒绝器 → 混合预测头联合建模帧内稳定性与帧间边界转移，抑制边界假阳性并输出最终预测。",
        "methods": "冻结基础模型适配（BiomedCLIP 编码器）；基于 nnU-Net 腹部区域概率的解剖加权空间池化；within-case 原型损失；三阶段级联精化（frame→segment→case-level rejecter）；混合预测头（帧稳定性 + 边界转移建模）；评估辅以嵌入几何分析与配对 bootstrap 置信区间。",
        "experiment": "在 ACOUSLIC-AI 基准上取得测试 F1 = 67.72，超过最强基础模型基线 FetalCLIP + PRS（F1 = 54.52，+13.20 F1）与最强视频时序动作检测基线 TriDet + PRS（+15.76 F1）；协同性（消融）研究显示原型损失单独使用使召回下降 12 点，与解剖加权池化组合后召回提升 6.5 点，呈现非可加的符号翻转现象。",
        "limitation": "以原文为准"
      }
    },
    {
      "title": "Decoupling Planning and Control for Instructable Agents",
      "authors": "Zineng Tang et al.",
      "venue": "arXiv 2026.08 · Published as a conference paper at COLM 2026. Project page: ",
      "summary": "该论文针对指令可遵循智能体中规划与控制的矛盾：指令微调的视觉语言模型（VLM）擅长从指令与观察生成高层计划，但难以在陌生环境中输出可靠的低延迟动作序列；而世界模型控制器擅长快速的观察到动作控制，却缺乏开放式任务引导。作者提出 Instruct-to-Act，将两者解耦结合：VLM 规划器稀疏地生成高层文本指令，世界模型控制器据此进行高频自主控制。为使控制器可被语言指令驱动，训练时对控制器策略轨迹片段用合成指令重标注，并将行为克隆目标与原有的奖励最大化和世界建模目标联合优化。该方法在多个具身环境（含多智能体环境，VLM 规划器通过语言协调、控制器充当执行器）中评估，在匹配的观察与动作空间下持续优于仅控制器和 VLM 直接生成动作的变体，保持快速控制且无需微调即可更换不同的预训练 VLM 规划器，并在绝大多数任务上（具体数量以原文为准）与强视觉-语言-动作及多智能体强化学习基线保持竞争力。",
      "paperUrl": "https://arxiv.org/abs/2608.26788",
      "score": 0.42,
      "category": "PLAN-CONTROL DECOUPLING × VLM规划器 × 世界模型控制器",
      "influence": "待补充",
      "figure": {
        "url": null,
        "caption": ""
      },
      "fields": {
        "background": "指令微调的视觉语言模型（VLM）能很好地将指令与观察映射为高层计划，但难以在陌生环境中将其实现为可靠的低延迟动作序列；世界模型控制器擅长快速的观察到动作控制，却缺乏开放式任务引导，两者各有短板。",
        "task": "构建指令可遵循的具身智能体系统 Instruct-to-Act：由 VLM 规划器生成稀疏、高延迟容忍的高层文本指令，世界模型控制器据此进行高频自主动作执行；并在多个具身环境（含多智能体环境）中验证。",
        "insight": "将规划与控制解耦可互补两者优势——用高层语义规划弥补控制器缺乏任务引导，用低延迟控制器弥补 VLM 动作生成不可靠；并通过合成指令重标注让本无语言接口的世界模型控制器变得可被指令驱动。",
        "pipeline": "VLM 规划器根据指令与观察生成稀疏高层文本指令 → 以该指令为条件，世界模型控制器以高频率自主输出动作 → 训练阶段对控制器策略 rollout 片段用合成指令重标注，联合优化行为克隆、奖励最大化与世界建模三个目标；多智能体场景中 VLM 规划器通过语言协调，控制器作为其执行器。",
        "methods": "世界模型控制器（观察到动作的高频控制）；VLM 高层规划器（生成稀疏文本指令）；合成指令对 rollout 片段进行重标注；行为克隆目标与奖励最大化目标、世界建模目标的联合优化；模块化解耦设计支持免微调更换预训练 VLM 规划器。",
        "experiment": "在多个具身环境（具体数量以原文为准，含多智能体环境）中评估；在匹配的观察与动作空间下，持续优于仅控制器与 VLM 直接生成动作两类变体，保持快速控制；可免微调更换不同预训练 VLM 规划器；与强视觉-语言-动作（VLA）及多智能体强化学习基线相比，在大多数任务上保持竞争力（具体比例以原文为准）。",
        "limitation": "与强 VLA 及多智能体强化学习基线相比，在少数任务上未能保持竞争力（即在七个任务中的一个上落后，具体以原文为准）；摘要未说明合成指令重标注与真实指令之间的分布差异及可扩展性等潜在问题。"
      }
    }
  ],
  "counts": {
    "total": 8,
    "new": 7
  }
};
