window.PAPER_DAILY_DATA = {
  "issue": "No.241",
  "date": "2026-08-29",
  "axes": "三维重建 × 世界模型",
  "edNote": "本期精选基于偏好画像筛选与排序。",
  "hero": {
    "title": "Thinking on Shots: Consistent Multi-Shot Video Editing with Agentic Reasoning",
    "titleZh": "以镜头为思考单元：智能体推理驱动的多镜头长视频编辑",
    "hook": "让AI像导演一样按镜头思考，一举消灭长视频编辑幻觉",
    "cards": [
      {
        "emoji": "🎯",
        "title": "问题与背景",
        "body": "生成式AI已显著推进视频编辑，但现有方法主要面向单镜头或短片段，带多条指令的长视频编辑仍是重大挑战。朴素的分块策略（如固定时长切分）会引发实体碎片化、严重的编辑幻觉以及时序连续性破坏。其困难在于三重约束的叠加：跨镜头内容需保持编辑一致，多条指令需相互解耦不串扰，且不能破坏原始时空结构。为此，作者提出`MMLVE`任务，将其归纳为跨镜头编辑一致性`CSEC`、多指令解耦`MID`与时空结构零破坏`ZDSS`三大核心目标。"
      },
      {
        "emoji": "⚙️",
        "title": "方法设计",
        "body": "核心是`MMLVE-Agent`智能体编辑框架，通过`LLM`与`VLM`的协同完成长视频编辑。框架首先执行`shot-level video decoupling`（镜头级视频解耦），依据语义边界而非固定时长划分镜头，从源头避免实体碎片化。随后进行`precise instruction parsing`（指令精准解析），将高密度异构指令分配并映射到对应的镜头与实体，实现多指令解耦。编辑在镜头级受控执行，再无缝拼接为完整输出，从而同时保障`CSEC`、`MID`与`ZDSS`三大目标。"
      },
      {
        "emoji": "📊",
        "title": "实验结果",
        "body": "为全面评测该任务，作者构建了`MMLVE-Bench`基准，其特点是复杂真实世界时空动态、高密度异构指令以及稀疏随机的实体分布，并设计了三项MMLVE专属评价指标。大量实验表明，`MMLVE-Agent`优于`Seedance 2.0`等闭源SOTA方法。具体而言，它成功消除了编辑幻觉，保持了跨镜头编辑一致性，并实现了无缝的时空过渡；具体量化数字详见原文。"
      },
      {
        "emoji": "⚠️",
        "title": "局限与展望",
        "body": "摘要中未明确列出作者承认的局限。从方法结构可推断其边界：`MMLVE-Agent`高度依赖`LLM`/`VLM`的解析与规划质量，指令理解偏差可能在镜头解耦与指令分配环节被放大；多模型协作的推理链路也可能带来较高的延迟与算力开销。此外，评测主要基于自建的`MMLVE-Bench`，跨领域与跨基准的泛化能力仍待进一步验证。"
      }
    ],
    "figureNote": "流程图从长视频输入出发，先由`VLM`参与的镜头级解耦模块按语义边界切分镜头，替代固定时长切块。随后`LLM`驱动的指令解析模块对高密度异构指令进行理解与分配，建立指令—镜头—实体的对应关系。最后各镜头编辑结果被拼接为完整输出，保证跨镜头一致与无缝时空过渡；具体模块细节以原文流程图为准。",
    "figures": [
      {
        "file": "2608_26809-fig1.jpg",
        "caption": "Figure 2: An overview of our MMLVE-Agent framework. The pipeline comprises three core modules: (1) Instruction &amp; Video Analysis, where the input long-video is segmented into physical shots via PyD",
        "kind": "pipeline"
      }
    ],
    "authors": "Chenyang Wu et al.",
    "venue": "arXiv 2026.08 · Project Page: https://wucy0519.github.io/MMLVE/ and see sour",
    "summary": "想象你要按一长串指令修改一部电影：换主角、改场景、调色调，还得保证几十个镜头前后一致——现有视频编辑模型处理几秒短片还行，碰上长片就乱套了。这篇论文将其正式定义为`MMLVE`任务，并提出`MMLVE-Agent`：像剪辑师先拆镜头再下指令那样，让`LLM`和`VLM`分工协作，完成镜头级解耦与指令精准解析。团队还构建了`MMLVE-Bench`基准与三项专属指标，结果显示它比`Seedance 2.0`等闭源SOTA更强，且能消除编辑幻觉。",
    "paperUrl": "https://arxiv.org/abs/2608.26809",
    "score": 0.59,
    "scores": {
      "innovation": 8,
      "effectiveness": 6
    },
    "category": "LONG-VIDEO EDITING × 智能体推理",
    "influence": "首提MMLVE任务并配套自建基准，公开叫板Seedance 2.0等闭源旗舰，有望成为长视频编辑方向的后续研究参照系。",
    "figure": {
      "url": "2608_26809-fig1.jpg",
      "caption": "Figure 2: An overview of our MMLVE-Agent framework. The pipeline comprises three core modules: (1) Instruction &amp; Video Analysis, where the input long-video is segmented into physical shots via PyD"
    },
    "fields": {
      "background": "生成式AI显著推进了视频编辑，但现有方法集中于单镜头或短视频片段；长视频多指令编辑仍是难题，固定时长等朴素分块策略会导致实体碎片化、严重编辑幻觉与时序连续性破坏。",
      "task": "提出`MMLVE`（多指令多镜头长视频编辑）任务，围绕三大核心目标：跨镜头编辑一致性`CSEC`、多指令解耦`MID`、时空结构零破坏`ZDSS`。",
      "insight": "将长视频编辑从端到端一次性生成转化为智能体推理问题：以镜头为思考单元，用`LLM`+`VLM`协同完成镜头级解耦与指令精准解析，从结构上规避幻觉与实体碎片化。",
      "pipeline": "长视频输入 → 镜头级视频解耦（`VLM`参与） → 指令解析与分配（`LLM`驱动） → 逐镜头受控编辑 → 无缝拼接输出，保障跨镜头一致与时空连续。",
      "methods": "`MMLVE-Agent`智能体编辑框架；`LLM`与`VLM`协同推理；`shot-level video decoupling`；`precise instruction parsing`；配套构建`MMLVE-Bench`基准与三项MMLVE专属指标。",
      "experiment": "在`MMLVE-Bench`上，`MMLVE-Agent`优于`Seedance 2.0`等闭源SOTA，成功消除编辑幻觉、保持跨镜头编辑一致性并实现无缝时空过渡；量化数字详见原文。",
      "limitation": "摘要未列明作者承认的局限；可推断边界包括：对`LLM`/`VLM`解析质量的依赖及误差放大风险、智能体推理链路的延迟与算力开销、评测依赖自建基准可能限制泛化结论。"
    }
  },
  "papers": [
    {
      "title": "TADP: Task-Aware Deformable Prediction for Single-Stage 3D Object Detection",
      "titleZh": "TADP：让特征按任务变形的单阶段3D目标检测",
      "hook": "让特征随任务『变形』，car mAP 达 80.91%",
      "cards": [
        {
          "emoji": "🎯",
          "title": "问题与背景",
          "body": "现有单阶段 3D 目标检测器通常将同一次提取的共享特征直接用于分类、边界框回归、朝向估计等多个任务。然而不同任务对特征的偏好存在本质差异，不存在一个对所有任务均最优的统一投影空间，特征共享引发的任务间冲突制约了检测性能上限。如何在保持单阶段检测高效性的同时实现任务自适应的特征利用，是本文的核心问题。"
        },
        {
          "emoji": "⚙️",
          "title": "方法设计",
          "body": "TADP 采用三段式架构。首先，`triple feature refinement aggregation` 模块自适应地提取三级特征，为后续任务提供差异化表征基础。其次，`multi-scale feature aggregation block` 以尺度感知方式融合多尺度特征，缓解尺度差异带来的信息不平衡。最后，即插即用的 `task-aware deformation head` 对各任务的预测施加可变形变换，显式感知各任务的侧重点与任务间交互。作者进一步设计了三种不同的变形模块以适配不同需求，且变形头可直接嵌入其他检测方法。"
        },
        {
          "emoji": "📊",
          "title": "实验结果",
          "body": "实验在 KITTI 数据集上进行，所提方法的 car mAP 达到 80.91%，超越该基准上众多 state-of-the-art 方法。迁移实验表明，所提出的变形头应用于其他检测方法时同样取得良好效果，验证了其即插即用的通用性。行人、骑行者等其他类别及各难度等级的细分结果详见原文。"
        },
        {
          "emoji": "⚠️",
          "title": "局限与展望",
          "body": "摘要中未明确讨论方法局限。从证据边界看，报告的主要结果集中于 KITTI 的 car 类别，对行人、骑行者等小目标类别以及 nuScenes、Waymo 等更复杂基准的泛化能力尚待验证；三种变形模块的选择准则与变形头引入的额外计算开销亦需原文进一步说明。"
        }
      ],
      "figureNote": "假设流程图展示方法全景：`triple feature refinement aggregation` 先自适应产出三级特征，交由 `multi-scale feature aggregation block` 完成尺度感知融合；融合特征随后送入各任务分支，经 `task-aware deformation head` 变形后输出对应预测。具体模块连接细节以原文流程图为准。",
      "figures": [
        {
          "file": "2608_27282-fig1.jpg",
          "caption": "Fig. 1: Visualization of detection in street scenes. It shows the different detection results of SECOND [ 5 ] and our TADP. We use red arrows to indicate the biased optimization of our method compared",
          "kind": "pipeline"
        }
      ],
      "authors": "Su Wang et al.",
      "venue": "arXiv 2026.08 · Accepted to the 2023 IEEE Intelligent Vehicles Symposium (IV",
      "summary": "想象流水线上一个工人用同一双手同时干质检、贴标、打包，难免顾此失彼——单阶段3D检测器也让分类、回归等所有任务挤在同一套特征上。这篇论文的解法是『各取所需』：先用 `triple feature refinement aggregation` 自适应抽取三级特征，再用 `multi-scale feature aggregation` 融合不同尺度信息，最后给每个任务配上即插即用的 `task-aware deformation head`，让特征按任务需要『变形』。得益于即插即用设计，这个变形头还能嫁接到其他检测器上。在 KITTI 数据集上，car mAP 达到 80.91%，把不少 SOTA 方法甩在身后。",
      "paperUrl": "https://arxiv.org/abs/2608.27282",
      "score": 0.49,
      "scores": {
        "innovation": 6,
        "effectiveness": 7
      },
      "category": "3D DETECTION × 任务感知可变形预测",
      "influence": "中文社区 B站 热议 · 摘要未披露作者与机构信息；方法为单阶段 3D 检测的模块化改进并依托 KITTI 基准验证，预计以社区内增量式引用与即插即用变形头的迁移应用为主。",
      "figure": {
        "url": "2608_27282-fig1.jpg",
        "caption": "Fig. 1: Visualization of detection in street scenes. It shows the different detection results of SECOND [ 5 ] and our TADP. We use red arrows to indicate the biased optimization of our method compared"
      },
      "fields": {
        "background": "单阶段 3D 目标检测器普遍以同一套共享特征服务分类、回归、朝向估计等多个任务，而特征无法在统一空间内对所有任务均最优，任务间冲突制约检测性能。",
        "task": "单阶段 3D 目标检测，在 KITTI 基准上验证，重点关注 car 类别。",
        "insight": "不同任务对特征的需求不同，应让每个任务的预测以可变形方式自适应地作用于特征，而非强行将所有任务映射到统一特征空间。",
        "pipeline": "三级特征自适应提取（triple feature refinement aggregation）→ 尺度感知多尺度融合→ 各任务分支经即插即用 task-aware deformation head 完成变形预测。",
        "methods": "triple feature refinement aggregation 模块、multi-scale feature aggregation block、task-aware deformation head（内含三种变形模块设计），plug-and-play 即插即用。",
        "experiment": "KITTI 数据集上 car mAP 80.91%，超越多项 SOTA；变形头在其他检测方法上亦验证有效。",
        "limitation": "摘要未明示局限；结果集中于 KITTI car 类，跨类别与跨数据集泛化、计算开销分析有待原文补充。"
      }
    },
    {
      "title": "R2M-Bench: Evaluating Revisit Memory via Relative Consistency in Interactive Video World Models",
      "titleZh": "画面没动≠记得住：R2M-Bench 重访记忆基准",
      "hook": "画面没动≠有记忆：相对一致性拆穿慢动作捷径",
      "cards": [
        {
          "emoji": "🎯",
          "title": "问题与背景",
          "body": "交互式视频世界模型的重访记忆通常以首访帧与返回帧的绝对相似度评测。然而该度量存在本质歧义：若中间 rollout 本身变化极小，重访对同样会呈现高相似度，未必反映模型记住了场景。因此绝对重访分数对渲染稳定性、重复内容与运动失效高度敏感，慢动作捷径即可造成虚高。如何区分重访特定一致性与一般时间稳定性，是可靠记忆评测必须解决的难题。"
        },
        {
          "emoji": "⚙️",
          "title": "方法设计",
          "body": "R2M-Bench 提出可观测的重访选择性一致性基准，核心思想是同 rollout 相对校准。对每个检测到的返回，基准从同一轨迹中构造两组对照：`gap-matched non-revisit pair` 度量一般时间稳定性基线，`short-range pair` 估计短程一致性。重访对相对时间基线的相似度优势定义为 `MemoryGain`（MG），再经 short-to-baseline 动态范围归一化得到 `Normalized Memory Ratio`（NMR）。基准由 100 个参考场景与 3 条 leave-and-return 轨迹组成 300 个实例，从外观保真度、场景与物体身份、局部几何与持久状态四个维度评测。整体设计将「记忆」操作化为超出一般稳定性的相对增益。"
        },
        {
          "emoji": "📊",
          "title": "实验结果",
          "body": "在 7 个动作条件视频世界模型上，Overall NMR 与人类一致性判断的 Spearman 相关系数为 ρ=0.547（95% CI [0.45, 0.63]）。NMR 在模型内与生成运动的相关性幅值为 0.072，而原始重访相似度为 0.207，表明相对校准显著削弱了慢动作捷径。在参评视频模型中，DreamX-World-Memo 取得最高的 Overall NMR。结果支持同 rollout 相对校准能够将重访特定一致性与一般时间稳定性区分开来。"
        },
        {
          "emoji": "⚠️",
          "title": "局限与展望",
          "body": "摘要未明示作者自述的局限。就方法边界而言，相对校准的有效性依赖对照组的可比性：若非重访片段与重访段在内容或动态上系统性失衡，MG 与 NMR 的解释力可能受限。此外，与人类判断的中等相关（ρ≈0.55）表明感知层面的对齐仍有差距。未来可扩展至更长重访间隔、更复杂交互以及跨场景记忆迁移的评测。"
        }
      ],
      "figureNote": "假设流程图展示方法全景：对每条 leave-and-return 轨迹中检测到的重访对，系统从同一 rollout 抽取 gap-matched 非重访对照对与 short-range 对照对，经外观保真、场景与物体身份、局部几何与持久状态的多维度量后，由重访相似度减去时间基线得到 MemoryGain，再按 short-to-baseline 动态范围归一化为 NMR。所得分数用于对 7 个动作条件世界模型排序，并与人类一致性判断对齐。",
      "figures": [
        {
          "file": "2608_27328-fig1.jpg",
          "caption": "Figure 2 : Overview of R2M-Bench. (a) Absolute first-visit/revisit similarity is not sufficient evidence of memory because motion magnitude and rendering stability can inflate the raw score. (b) R2M-B",
          "kind": "pipeline"
        }
      ],
      "authors": "Qiwen Gu et al.",
      "venue": "arXiv 2026.08 · Code: https://github.com/AMAP-ML/R2MBench",
      "summary": "想象你在游戏里离开一个房间再折返，发现画面和原来一模一样——这真能说明 AI「记得」这个房间吗？未必，也可能它生成的画面本来就几乎不动（比如动作失效变成慢动作）。这篇论文提出 `R2M-Bench`：不看「重访帧像不像」，而是像做对照实验，从同一条 `rollout` 里挑一对非重访帧和一对近距离帧当参照组，看重访带来的相似度增益是否超出基线。由此得到 `MemoryGain` 和 `Normalized Memory Ratio` 两个指标，把「真记忆」和「画面本来就稳」区分开。",
      "paperUrl": "https://arxiv.org/abs/2608.27328",
      "score": 0.48,
      "scores": {
        "innovation": 8,
        "effectiveness": 7
      },
      "category": "BENCHMARK × 视频世界模型记忆",
      "influence": "摘要未披露团队机构；作为首个以相对一致性解耦重访记忆与时间稳定性的基准，评测覆盖 7 个主流动作条件世界模型，具备成为记忆维度标准评测协议的潜力。",
      "figure": {
        "url": "2608_27328-fig1.jpg",
        "caption": "Figure 2 : Overview of R2M-Bench. (a) Absolute first-visit/revisit similarity is not sufficient evidence of memory because motion magnitude and rendering stability can inflate the raw score. (b) R2M-B"
      },
      "fields": {
        "background": "交互式视频世界模型的记忆能力常以首访与返回帧的绝对相似度评测，但该指标与渲染稳定性、重复内容及运动失效混淆，慢动作捷径可致分数虚高。",
        "task": "构建能区分「重访特定一致性」与「一般时间稳定性」的基准，可靠评测动作条件视频世界模型的重访记忆。",
        "insight": "在同一 rollout 内引入 gap-matched 非重访对照与 short-range 对照，将重访相似度转化为相对增益（MemoryGain）并按动态范围归一化（NMR），即可剥离时间稳定性混淆。",
        "pipeline": "检测返回帧 → 从同轨迹抽取 gap-matched 非重访对照对与 short-range 对照对 → 多维度度量一致性 → 计算 MG 并归一化为 NMR → 在 300 个实例上评测 7 个模型并与人类判断对齐。",
        "methods": "R2M-Bench 基准；MemoryGain（MG）；Normalized Memory Ratio（NMR）；gap-matched non-revisit pair 与 short-range pair 双重对照设计；100 参考场景 × 3 条 leave-and-return 轨迹 = 300 实例；评测维度涵盖外观保真、场景与物体身份、局部几何、持久状态。",
        "experiment": "7 个动作条件视频世界模型上，Overall NMR 与人类一致性判断 Spearman ρ=0.547（95% CI [0.45, 0.63]）；模型内与生成运动相关性为 0.072（原始重访相似度为 0.207），显著削弱慢动作捷径；DreamX-World-Memo 获最高 Overall NMR。",
        "limitation": "摘要未列作者自述局限；相对校准依赖对照组可比性，且与人类判断仅中等强度相关（ρ≈0.55），感知对齐与更复杂交互场景仍有扩展空间。"
      }
    },
    {
      "title": "Glass Surface Detection Grounded in 3D Visual Geometry",
      "titleZh": "玻璃不再隐形：以3D视觉几何为锚的玻璃表面检测",
      "hook": "让隐形玻璃现形：从看“外表”到量“几何”的范式转变",
      "cards": [
        {
          "emoji": "🎯",
          "title": "问题与背景",
          "body": "玻璃表面检测（GSD）是场景理解与三维重建的关键环节，但玻璃的透明性与反光性使其成为视觉感知的顽固盲区。现有方法普遍依赖二维外观线索，在几何歧义场景中极易失效：玻璃背后的景物外观与真实表面相互混淆，缺乏可靠的判别依据。其根本困难在于玻璃在2D图像层面“看似不存在”。该工作据此提出范式转变——将GSD锚定于三维视觉几何，从物理存在性层面显式建模玻璃表面。"
        },
        {
          "emoji": "⚙️",
          "title": "方法设计",
          "body": "方法首先从视觉几何接地 Transformer（`VGGT`）中蒸馏丰富的3D先验，生成玻璃感知的三维表征。在此之上构建多任务学习框架，并设计新颖的玻璃检测头。检测头包含两个核心模块：`FSAM`（Frequency Self-Attention Module）通过频率自注意力识别玻璃特有的谱特征，服务于玻璃表面定位；`GeGB`（Geometry Grounding Block）将二维特征选择性地接地到三维几何，完成玻璃表面分割。整体上，“频域定位”与“几何接地分割”形成互补的双通道设计，并经多任务学习联合优化。"
        },
        {
          "emoji": "📊",
          "title": "实验结果",
          "body": "作者在七个标准GSD基准上开展广泛实验，方法均取得state-of-the-art性能。实验进一步验证了对视频与多模态数据的良好泛化能力。在含玻璃场景的三维重建任务中，方法带来显著改善。摘要未给出具体指标数值，详细对比与消融详见原文；代码已在GitHub开源。"
        },
        {
          "emoji": "⚠️",
          "title": "局限与展望",
          "body": "摘要未明确列举方法局限。基于机制判断：性能依赖`VGGT`所提供3D先验的质量，在几何估计失效的极端场景（如强反光、完全无纹理的透明面）中可能连带受损；`FSAM`的频域分析对图像分辨率与压缩伪影的敏感性亦有待检验。未来方向包括更轻量的几何先验蒸馏、跨域泛化与实时性优化。"
        }
      ],
      "figureNote": "流程图应呈现方法全景：输入先经`VGGT`蒸馏3D先验，生成玻璃感知的3D表征；该表征随后流入多任务玻璃检测头，其中`FSAM`以频率自注意力捕捉玻璃特有谱特征完成定位，`GeGB`将2D特征选择性接地至3D几何完成分割。定位与分割两路经多任务学习联合优化并输出最终检测结果；具体模块排布以原文流程图为准。",
      "figures": [
        {
          "file": "2608_26752-fig1.jpg",
          "caption": "Figure 1 . SOTA GSD methods typically rely on 2D appearance cues ( e.g. , by explicitly modeling the ghosting effects ( Yan et al., 2025 ) ) or implicitly learning glass-specific embeddings from other",
          "kind": "pipeline"
        }
      ],
      "authors": "Yiwei Lu et al.",
      "venue": "arXiv 2026.08 · 9 pages, 10 figures. Accepted by ACM Multimedia 2026",
      "summary": "想象扫地机器人一头撞上玻璃门——玻璃在摄像头眼里几乎“不存在”，只看2D外观的方法完全被骗。这篇论文干脆换思路：请出视觉几何基础模型`VGGT`当“透视眼”，在3D几何空间里显式建模玻璃的物理存在。再配上捕捉玻璃独特“光谱指纹”的`FSAM`、把2D特征钉进3D几何的`GeGB`，玻璃的位置和边界一清二楚。最终在七个标准基准上全面刷新SOTA，还顺手救活了玻璃场景的三维重建。",
      "paperUrl": "https://arxiv.org/abs/2608.26752",
      "score": 0.48,
      "scores": {
        "innovation": 8,
        "effectiveness": 7
      },
      "category": "3D VISUAL GEOMETRY × GLASS DETECTION",
      "influence": "依托视觉几何基础模型`VGGT`（CVPR 2025最佳论文）的研究热度，代码开源可复现，兼具基础模型势能与应用落地价值。",
      "figure": {
        "url": "2608_26752-fig1.jpg",
        "caption": "Figure 1 . SOTA GSD methods typically rely on 2D appearance cues ( e.g. , by explicitly modeling the ghosting effects ( Yan et al., 2025 ) ) or implicitly learning glass-specific embeddings from other"
      },
      "fields": {
        "background": "玻璃表面检测（GSD）是场景理解与重建的关键任务，但玻璃的透明与反光使依赖2D外观线索的已有方法在几何歧义场景中失效",
        "task": "玻璃表面检测与分割，并拓展至视频/多模态泛化及含玻璃场景的三维重建",
        "insight": "将GSD从2D外观范式转向3D视觉几何，显式建模玻璃表面的物理存在性",
        "pipeline": "`VGGT`蒸馏3D先验→生成玻璃感知3D表征→多任务玻璃检测头（`FSAM`频域定位＋`GeGB`几何接地分割）",
        "methods": "3D先验蒸馏、频率自注意力模块（`FSAM`）、几何接地块（`GeGB`）、多任务学习",
        "experiment": "在七个标准GSD基准上均达到SOTA；泛化至视频与多模态数据；显著提升含玻璃场景的三维重建（具体数值详见原文）",
        "limitation": "摘要未明示局限；效果依赖`VGGT`先验质量，极端反光与无纹理透明面的鲁棒性待验证"
      }
    }
  ],
  "counts": {
    "total": 4,
    "new": 3
  }
};
