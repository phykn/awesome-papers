# Zip-NeRF: Anti-Aliased Grid-Based Neural Radiance Fields
- **Authors**: Jonathan T. Barron, Ben Mildenhall, Dor Verbin, Pratul P. Srinivasan, Peter Hedman
- **Venue/Date**: ICCV 2023
- **URL**: https://arxiv.org/abs/2304.06706
- **GitHub**: https://github.com/google-research/zip-nerf

### 1. 背景
标准神经辐射场 (NeRF) 面临两个主要问题：训练/渲染速度慢以及锯齿（走样）。Mip-NeRF 通过圆锥台解决了走样问题，但速度较慢。Instant NGP 引入了快速的基于网格的表示，但由于采用离散点采样，又带回了走样问题。Zip-NeRF 旨在整合两者的优点：网格的速度和圆锥台的抗走样性能。

### 2. 直觉
想象一下尝试用一支非常细的笔在网格上着色（基于网格的 NeRF）。如果你稍微移动一下画笔，颜色就会突变（走样）。Zip-NeRF 就像在每个像素上使用多个小画笔，并在将颜色应用到网格之前平均它们的颜色，无论你怎么移动都能确保平滑过渡。

### 3. 核心突破
核心突破是一种多重采样策略，它将 Instant NGP 的网格金字塔集成到 mip-NeRF 360 的框架中。通过使用六边形多重采样模式和预过滤损失，模型可以在不牺牲哈希编码速度的情况下“推理”网格体素的尺度。

### 4. 技术机制

#### 4.1 Pipeline
![Pipeline Figure](figures/fig02_pipeline.png)
- 该流水线集成了多分辨率哈希网格与多重采样策略。不是采样单个点，而是按六边形模式在每个间隔采样 6 个点，以表示圆锥台体积。
- 核心模块：多分辨率哈希网格与每个截锥体 6 点六边形多重采样的组合。

#### 4.2 Architecture / Core Design
![Architecture Figure](figures/fig03_architecture.png)
- 架构使用了多重采样特征化，网格特征在样本之间进行平均。这使得 MLP 能够接收到与该深度网格分辨率匹配的“尺度感知”输入。
- 设计理由：尺度感知输入特征化可防止高频噪声泄漏到 MLP 中 (图 3)。

#### 4.3 Core Equation
- 尺度感知特征 $f$ 通过对多个样本的三线性插值哈希网格特征取平均进行计算：
- $$f(\mathbf{x}, \sigma) = \frac{1}{J} \sum_{j=1}^{J} \text{tri}(\text{hash}(\mathbf{x}_j))$$
- Variables:
- $\mathbf{x}_j$: 圆锥台内的第 $j$ 个多重采样坐标 (图 3)。
- $\sigma$: 决定样本扩散程度的尺度参数。
- $\text{tri}$: 哈希网格特征上的三线性插值 (等式 2)。
- $J$: 样本数量 (本文固定为 6)。

#### 4.4 Comparison: Others vs This Paper
Zip-NeRF 的性能显著优于 mip-NeRF 360 和 Instant NGP。虽然 mip-NeRF 360 提供了高质量的抗走样，但对于大规模训练来说速度太慢。Instant NGP 速度快，但在放大或缩小时会产生严重的走样伪影（锯齿）（第 4.1 节）。Zip-NeRF 在训练速度比 mip-NeRF 360 快 24 倍的同时，实现了更低的错误率（降低了 8% 到 77%）（图 1）。主要的权衡是由于多重采样特征导致的内存占用略高，但速度和质量的提升非常显著。

#### 4.5 Qualitative Results
![Qualitative Results](figures/fig01_teaser.png)
- 定性结果表明，Zip-NeRF 在恢复叶子和栏杆等精细结构方面表现出色，而这些结构在基于网格的模型中通常会丢失或走样。与地面真值 (图 1) 的比较显示，Zip-NeRF 的渲染效果几乎与真实图像无异，而之前的快速方法则表现出明显的闪烁和噪声。

### 5. 影响
Zip-NeRF 为高效、高质量的视图合成设定了新标准。它弥合了“研究级”质量与“生产级”速度之间的鸿沟，使辐射场在 VR 和高端数字孪生等实际应用中更加实用。

### 6. 延伸阅读

[1] [Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields (2021)](https://arxiv.org/abs/2111.12077)<br>
引入非线性场景收缩和抗走样圆锥截锥体，处理无界场景的前驱研究。<br>
[2] [Instant Neural Graphics Primitives with a Multiresolution Hash Encoding (2022)](https://arxiv.org/abs/2201.05989)<br>
引入了 Zip-NeRF 针对抗走样优化的快速哈希网格特征化方法。<br>
[3] [3D Gaussian Splatting for Real-Time Radiance Field Rendering (2023)](https://arxiv.org/abs/2308.04079)<br>
使用显式点基元替代体积场的竞争性最新方法。<br>
[4] [MERF: Memory-Efficient Radiance Fields for Real-Time View Synthesis (2023)](https://arxiv.org/abs/2302.12249)<br>
专注于实时浏览器端辐射场渲染的混合表示方法。<br>
[5] [NeRF: Representing Scenes as Neural Radiance Fields (2020)](https://arxiv.org/abs/2003.08934)<br>
开创神经辐射场革命的奠基性论文。<br>

