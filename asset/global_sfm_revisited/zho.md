
# Global Structure-from-Motion Revisited
- **Authors**: Linfei Pan, Dániel Baráth, Marc Pollefeys, Johannes L. Schönberger
- **Venue/Date**: arXiv 2024
- **URL**: [https://arxiv.org/abs/2407.20219](https://arxiv.org/abs/2407.20219)
- **GitHub**: [https://github.com/colmap/glomap](https://github.com/colmap/glomap)

---

### 1. 背景
运动恢复结构 (SfM) 是从多张图像中重建三维结构和相机位姿的过程。传统方法分为**增量式 SfM**（精确但由于重复优化 [Bundle Adjustment] 而速度缓慢）和**全局式 SfM**（速度快但容易失败）。全局式 SfM 的主要弱点在于“平移平均化”步骤，即从相对方向估计相机位置。这一步骤在数学上通常是病态的 (Ill-posed)，对相机内参误差高度敏感，并且在直线运动等常见运动模式下经常失败。

### 2. 直觉
想象一下在组装一个大型复杂的乐高模型。增量式 SfM 就像是每增加一块积木都要检查一次整体对齐情况——非常精确，但耗时极长。传统的全局式 SfM 就像是先分别组装好各个小的子模块，然后仅根据它们指向的方向尝试将它们拼凑在一起——如果一个方向稍有偏差，整个模型就会崩溃。**GLOMAP** 的直觉是在定位阶段同时放置相机和它们连接的锚点（三维点）。通过在定位过程中将相机直接与三维点关联，系统变得更加稳定和精确，类似于骨架如何支撑身体。

### 3. 突破
GLOMAP 的核心突破是引入了**联合全局定位** (Joint Global Positioning) 步骤。GLOMAP 不再遵循“旋转平均 $\rightarrow$ 平移平均 $\rightarrow$ 三角测量”的标准化全局 SfM 顺序，而是执行**联合相机和点位估计**。通过丢弃有问题的相对平移约束，转而共同优化相机光线和三维点，该方法比以前的全局方法更鲁棒地处理未知相机内参和退化运动模式，有效地缩小了与增量式 SfM 在准确性上的差距。

### 4. 技术机制

#### 4.1 流水线
![Pipeline Figure](figures/fig02_pipeline.png)
- 流水线始于特征匹配和双视图几何验证，随后通过旋转平均找到相机方向。核心创新发生在**全局定位**阶段，在该阶段共同求解相机位置和三维点位置，然后进行最终精细化。
- (1) 端到端 GLOMAP 系统架构概览。(2) “全局定位”模块（第 3.2 节）是区别于传统流水线的关键。

#### 4.2 架构 / 核心设计
![Architecture Figure](figures/fig03_architecture.png)
- 该图展示了从随机初始状态到结构化三维配置的转变。通过最小化观测到的相机光线 ($v_{ik}$) 与计算出的相机到点向量之间的角度差异，系统收敛到全局一致的几何结构。
- (1) 全局定位优化过程的可视化。(2) 使用基于光线的约束而非相对平移，允许更鲁棒的收敛。

#### 4.3 核心方程
- **选择标准**: 方程 (3) 是实现相机和点联合估计的主要优化目标，这是 GLOMAP 的定义性特征。
- **方程**:
  
  $$\underset{\mathbf{X}, \mathbf{c}, \mathbf{d}}{\arg\min} \sum_{i,k} \rho (\|\mathbf{v}_{ik} - d_{ik}(\mathbf{X}_k - \mathbf{c}_i)\|^2), \text{ subject to } d_{ik} \ge 0$$
  
- 该公式表示观测到的方向光线与连接相机和点的向量之间距离的加权最小化。
- **变量**: 
  - $\mathbf{X}_k$: 第 $k$ 个特征轨迹的三维位置（第 3.2 节）。
  - $\mathbf{c}_i$: 第 $i$ 个相机的三维位置（第 3.2 节）。
  - $\mathbf{v}_{ik}$: 观测 $(i, k)$ 的全局旋转相机光线（方程 3）。
  - $d_{ik}$: 考虑点距离未知的每个观测缩放因子（方程 3）。
  - $\rho$: 用于减轻异常匹配影响的 Huber 鲁棒核函数（第 3.2 节）。

#### 4.4 比较：其他方法 vs 本文
GLOMAP 达到的准确性和鲁棒性水平与目前使用最广泛的增量式 SfM 系统 COLMAP 相当甚至更优，同时运行速度快了几个数量级。与以前的全局 SfM 系统（如 Theia）不同，GLOMAP 通过避免病态的平移平均步骤，能够可靠地处理具有未知内参的互联网照片集或序列数据。特别是在 IMC 2023 数据集上，其结果的 AUC 分数明显高于其他全局基准，且速度约为 COLMAP 的 8 倍（第 4.2 节 / 表 5）。本文的差异化在于它能够在不牺牲增量方法重建质量的情况下保持全局方法的扩展性。

#### 4.5 定性结果
![Qualitative Results](figures/fig01_teaser.png)

定性结果证明了 GLOMAP 在从互联网照片集到结构化序列捕获的各种数据集上产生密集且准确的三维重建的能力。在 LaMAR 数据集的并行比较中，GLOMAP 成功重建了当前全局基准（如 Theia）无法产生一致模型的复杂场景，甚至超过了增量系统（如 COLMAP）的完整性（图 1b）。视觉证据表明，GLOMAP 产生的伪影更少，几何结构更完整，特别是在大规模环境中。这种鲁棒性归功于其联合优化策略，该策略能更好地处理噪声和比例不一致。

### 5. 影响
GLOMAP 证明了全局方法在通用用途上可以像增量方法一样可靠，从而重塑了 SfM 的研究图景。这是大规模三维制图的一次重大飞跃，因为它能够使在几分钟而不是几小时内处理数千张图像成为可能，且没有典型的重建失败风险。作为 COLMAP 生态系统的一部分开源，它有望成为计算机视觉研究人员和从事新视图合成（如 NeRF 和 Gaussian Splatting）及大规模数字孪生工作的工程师的标准工具。

### 6. 延伸阅读
- [FastMap: Revisiting Structure from Motion through First-Order Optimization](https://arxiv.org/abs/2505.04612) - 2025 年的一项后续研究，使用一阶优化实现了比 GLOMAP 快 10 倍的速度。
- [Gravity-Aligned Rotation Averaging with Circular Regression](https://arxiv.org/abs/2410.12763) - GLOMAP 作者 2024 年的一项工作，结合了重力先验以进一步改进旋转平均。
- [MP-SfM: Monocular Surface Priors for Robust Structure-From-Motion](https://arxiv.org/abs/2504.20040) - 2025 年的一篇论文，探索使用单目表面先验来增强复杂场景下 SfM 的鲁棒性。
