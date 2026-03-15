# FVO: Fast Visual Odometry with Transformers

- **Authors**: Vladimir Yugay, Duy-Kien Nguyen, Theo Gevers, Cees G. M. Snoek, Martin R. Oswald
- **Venue/Date**: arXiv 2026 (2026年3月9日发布) / ICLR 2026 (预印本)
- **URL**: [https://arxiv.org/abs/2510.03348](https://arxiv.org/abs/2510.03348)
- **GitHub**: [https://vladimiryugay.github.io/fvo](https://vladimiryugay.github.io/fvo)

---

### 1. 背景

传统的单目视觉里程计（Visual Odometry, VO）系统通常构建为混合流水线，将用于特征提取的研究深度神经网络与传统的几何优化（如**捆绑调整**，Bundle Adjustment）相结合。虽然这些方法精度较高，但面临两个主要瓶颈：由于迭代优化，计算成本昂贵；且在没有外部校准的情况下，难以估计绝对度量尺度（Metric Scale）。最近，像 DUSt3R 这样的大型 3D 模型在几何理解方面展示了潜力，但它们对于连续视频流来说速度太慢，或者缺乏必要的时间一致性。因此，迫切需要一种既能实现端到端，又足够快以满足实时应用需求的 VO 系统。

### 2. 直觉

想象你正穿过一个拥挤的火车站。为了弄清楚你要去哪里，你不会为每一块砖头和每一个人构建一个完美的 3D 地图；相反，你会通过观察风景随时间的变化来本能地感知自己的相对运动。更重要的是，你知道什么时候该相信自己的眼睛——如果你正走过一堵纯白色的墙，你会意识到你的运动感不太可靠，并更多地依赖其他线索。FVO 的工作原理就像这个“直觉导航员”。它用一个直接“感受”帧间相对运动、同时学习预测自身不确定性的 Transformer 替代了死板的几何数学公式。

### 3. 技术突破

FVO 的决定性洞察在于将视觉里程计建模为一个直接的**相对姿态回归**（Relative Pose Regression）问题，并结合了学习到的**异方差不确定性**（Heteroscedastic Uncertainty）。FVO 不再将 VO 视为一个重建并优化的任务，而是使用高容量 Transformer 将重叠的图像窗口直接映射到相机轨迹。这一突破的关键在于**置信度感知推理方案**（Confidence-aware Inference Scheme）：通过预测模型对每个相对姿态的确定程度，模型可以稳健地将数百个重叠的预测聚合为一个平滑的全域轨迹，从而有效地用简单的加权平均过程替代了昂贵的捆绑调整。

### 4. 技术机制

#### 4.1 流水线

![Pipeline Figure](figures/fig01_pipeline.png)

- FVO 通过高效的 Transformer 处理简短且重叠的视频窗口，以估计相对姿态和置信度分数。这些局部估计随后由推理模块融合为一致的度量轨迹。
- (1) 该图展示了从原始视频帧到统一的度量相机轨迹的转换。 (2) 重叠窗口允许模型通过冗余和置信度加权来细化其估计。

#### 4.2 架构 / 核心设计

![Architecture Figure](figures/fig02_architecture.png)

- 该架构由一个冻结的预训练编码器（源自 CroCo/DUSt3R）以及一个具有重复时间合空间注意块的**时空解码器**（Time-Space Decoder）组成。它使用可学习的相机 Token 来聚合整个序列的信息。
- (1) 该图说明了从单图 Token 嵌入到最终姿态和置信度头的数据流。 (2) 在 $SO(3)$ 流形上预测旋转，确保所有相对旋转在数学上始终有效。

#### 4.3 核心公式

该网络使用集成了旋转和平移的可学习不确定性参数 $c\_R, c\_t$ 的**置信度感知损失函数**（Confidence-Aware Loss）进行训练。这使得模型能够通过降低其识别为噪声或不可靠残差的权重来实现“自我校准”。


$$ \mathcal{L} = \mathcal{L}\_{\text{rot}} \exp(-c\_R) + c\_R + \mathcal{L}\_{\text{trans}} \exp(-c\_t) + c\_t $$

- $\mathcal{L}\_{\text{rot}}$: 预测旋转矩阵与真实旋转矩阵之间的测地线损失 (Eq 9)。
- $\mathcal{L}\_{\text{trans}}$: 预测相对平移与真实值之间的 $L1$ 损失 (Eq 10)。
- $c\_R, c\_t$: 分别代表旋转和平移不确定性的学习对数方差参数 (Sec 3.3)。
- $\exp(-c)$: 精度项，根据预测的置信度自动加权误差的重要性 (Sec 3.3)。


#### 4.4 比较：其他方法 vs 本文 (基于证据)

FVO 在不牺牲精度的情况下，代表了 VO 效率的一次重大飞跃。虽然像 DPVO 这样强大的基准方法依赖于复杂的捆绑调整循环，使其速度限制在约 35 FPS，但 FVO 在相同硬件上达到了近 76 FPS——速度提高了 2 倍 (Table 1)。与 VGGT 或 MASt3R-SLAM 等由于尺度模糊或长序列内存限制而挣扎的大规模模型不同，FVO 通过利用其置信度感知聚合来维持稳健的度量轨迹 (Sec 4.1)。来自 ScanNet 和 ARKit 基准测试的证据表明，FVO 在绝对轨迹误差 (ATE) 方面优于所有非优化基准，同时与最佳混合方法保持竞争力 (Table 1)。唯一提到的权衡是其对静态环境的关注；其在高度动态场景中的表现仍是未来的研究方向 (Sec 5)。

#### 4.5 质性结果

![Qualitative Results](figures/fig07_qualitative.png)

在 ScanNet 和 ARKit 上的质性轨迹结果证明了 FVO 与现有的端到端模型相比具有卓越的稳健性。如 图 7 所示，FVO（以青色显示）在复杂的圆形和线性运动中紧密跟踪真实轨迹（虚线），而早期的模型如 TSFormer 和 CUT3R 则表现出明显的漂移或完全失败。值得注意的是，FVO 成功地在不同序列中保持了绝对尺度，而无需任何针对每个数据集的手动调整。颜色编码显示，FVO 始终将 ATE RMSE 保持在较低水平（主要在蓝色范围内），而基准方法在急转弯或低纹理段经常飙升至高误差的红色区域。在极长距离的轨迹中可以看到一个小限制，即仍能观察到轻微的累积漂移 (Fig 7, 底行)。

### 5. 影响

FVO 为新一代纯学习型 SLAM 系统铺平了道路，这些系统快速、稳健且无需校准。通过证明精心设计的 Transformer 可以替代传统的几何优化块，它消除在低功耗移动设备和机器人上部署高性能 VO 的主要障碍。其端到端的特性简化了工程栈，使视觉里程计更容易集成到用于自主导航和增强现实的更广泛的多模态智能系统中。

### 6. 延伸阅读
[1] [LEVIO: Lightweight Embedded Visual Inertial Odometry for Resource-Constrained Devices (2026)](https://arxiv.org/abs/2602.03294)<br>
一种针对超低功耗嵌入式平台的高度优化的 VIO 流水线，挑战了效率的极限。
[2] [OpenVO: Open-World Visual Odometry with Temporal Dynamics Awareness (2026)](https://arxiv.org/abs/2602.19035)<br>
探索了使用时间编码在仪表盘摄像头片段等未校准的开放世界环境中的视觉里程计。
[3] [MDE-VIO: Enhancing Visual-Inertial Odometry Using Learned Depth Priors (2026)](https://arxiv.org/abs/2602.11323)<br>
将深度学习得到的深度先验集成到传统的 VIO 后端中，以提高在低纹理环境中的稳健性。
