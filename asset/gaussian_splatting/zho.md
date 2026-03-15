# 3D Gaussian Splatting for Real-Time Radiance Field Rendering

- **作者**: Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, George Drettakis
- **会议/日期**: SIGGRAPH 2023 / 2023年8月
- **URL**: [https://arxiv.org/abs/2308.04079](https://arxiv.org/abs/2308.04079)
- **GitHub**: [https://github.com/graphdeco-inria/gaussian-splatting](https://github.com/graphdeco-inria/gaussian-splatting)

---

### 1. 背景
神经辐射场 (NeRF) 通过使用连续体积函数 (MLP) 表示密度和颜色，彻底改变了 3D 场景重建。然而，NeRF 面临着严重的渲染速度与质量的权衡：每个像素需要数以千计的高昂神经网络查询，使得实时渲染极具挑战。虽然最近的方法如 Instant-NGP 或 Plenoxels 通过网格结构提高了速度，但在处理复杂、大尺度场景的精细细节和高频背景时往往力不从心。因此，需要一种新方法来弥合“高质量”与“实时交互性能”之间的鸿沟。

### 2. 直觉
想象你是一位画家，试图表现一个 3D 场景。你不再是填充 3D 网格中的每一个点（体素），也不是试图用一个复杂的数学公式描述整个场景 (NeRF)，而是使用一系列模糊、半透明的**“喷漆点”** (3D 高斯)。有些点是圆形的，而有些点则像针一样被拉得很细（各向异性），以贴合桌子的边缘或叶子的表面。通过将数百万个这些彩色“泼溅点” (splats) 相互叠加，你可以非常快速地从任何角度重建复杂的图像，就像传统计算机图形学渲染三角形一样快，但同时具备照片般的柔和度。

### 3. 突破
本研究的核心洞见是用**可微 3D 高斯泼溅**和高性能**基于瓦片的着色器 (Tile-based Rasterizer)** 替代了 NeRF 中昂贵的体素光线投射 (Volumetric Ray-marching)。通过将场景表示为一组可以投影到 2D 的数百万个显式椭球体，作者实现了利用硬件加速的排序和混合。这种从隐式（查询函数）到显式（绘制基元）的转变，使得他们能够在保持顶级 NeRF 模型视觉质量的同时，实现超过 100 FPS 的渲染速度。

### 4. 技术机制

#### 4.1 流水线
![Pipeline Figure](figures/fig02_pipeline.png)
- 工作流程从运动恢复结构 (SfM) 生成的稀疏点云开始，这些点云被转换为一组 3D 高斯。然后通过快速的瓦片化可微着色器，对这些高斯的 位置、旋转、缩放、不透明度和颜色（球谐函数）进行优化，以实现实时反馈。
- (1) 该图展示了从稀疏输入点到密集、优化后的辐射场的端到端转换过程。(2) 请注意“自适应密度控制 (Adaptive Density Control)”步骤，这对于填充场景中的空白至此重要。

#### 4.2 架构 / 核心设计
![Architecture Figure](figures/fig04_densification.png)
- 系统的核心逻辑是**自适应高斯致密化 (Adaptive Gaussian Densification)**。模型不是使用固定数量的高斯，而是动态地在场景复杂或重建不足的地方创建更多“泼溅点”。它会“克隆”小的、重建不足区域的高斯，并“拆分”大的、模糊的高斯，从而捕获极细微的细节。
- (1) 此图说明了模型如何识别“重建不足”与“过度重建”区域。(2) 通过“拆分”和“克隆”操作，模型能够根据场景复杂度自动调整分辨率。

#### 4.3 核心方程
- **选择标准**: 该方程描述了 3D 协方差矩阵（高斯的形状）是如何参数化的，以便在通过梯度下降进行安全优化的同时，保持物理上的有效性（正定性）。
- **方程**: $\Sigma = R S S^T R^T$
- 该公式将高斯椭球的形状分解为两个独立的组成部分：拉伸（缩放 $S$）和方向（旋转 $R$）。
- **变量**:
  - $\Sigma$ = 代表高斯形状和大小的 3D 协方差矩阵。
  - $R$ = 由优化后的单位四元数 $q$ 推导出的旋转矩阵。
  - $S$ = 由优化后的 3D 向量 $s$ 推导出的缩放矩阵。

#### 4.4 对比分析：其他方法 vs 本论文
3D 高斯泼溅代表了从隐式神经体积到显式点基泼溅的范式转换。最强的基准模型 Mip-NeRF360 提供了出色的图像质量，但渲染一帧需要数分钟。相比之下，本文在实现实时渲染的同时，达到了同等甚至更好的质量 (Sec 7.1)。通过摆脱基于 MVS 的几何并选择各向异性高斯，该方法避免了点云渲染中常见的伪影 (Fig 11)，并减少了密集网格的训练开销。主要权衡是存储数百万个高斯所需的内存，复杂场景可能达到数 GB (Sec 7.5)。

#### 4.5 定性结果
![Qualitative Results](figures/fig05_qualitative.png)
结果表明，该方法在重建精细、纤薄的结构（如自行车的辐条或花园里的叶子）方面表现出色，而之前的 Instant-NGP 等方法通常会产生模糊或“像素化”的伪影。在与 Mip-NeRF360 的并排对比中，两者的清晰度和视点相关反射在视觉上几乎无法区分。正如在“Bicycle”和“Garden”场景中所见，我们的方法比 Plenoxels 更好地保留了金属表面的镜面高光和自然物体的复杂纹理 (Table 1 / Fig 5)。一个局限性是在视点相关效应未完全收敛的极端稀疏区域，偶尔会出现“针状”伪影。

### 5. 影响
本论文实际上终结了高质量辐射场的高额渲染成本时代。通过提供实时、可微的着色流水线，它为虚拟现实 (VR)、数字孪生和实时电影级渲染铺平了道路。3D 高斯泼溅现已成为显式辐射场研究的新标准，催生了数十项关于压缩、动画和大规模制图的后续工作。

### 6. 延伸阅读
- [SuGaR: Surface-Aligned Gaussian Splatting](https://arxiv.org/abs/2311.16523) - 一种通过将高斯对齐到场景表面来提取高质量网格的方法。
- [4D Gaussian Splatting for Real-Time Dynamic Scene Rendering](https://arxiv.org/abs/2310.08585) - 将该表示扩展到具有移动物体的动态场景。
- [GaussianPro: 3D Gaussian Splatting with Progressive Propagation](https://arxiv.org/abs/2402.14650) - 改进了密度控制机制，在复杂几何上实现更好的质量。
- [Compact 3D Gaussian Splatting](https://arxiv.org/abs/2311.13681) - 通过压缩高斯表示来解决内存瓶颈问题。
- [Zip-NeRF: Anti-Aliased Grid-Based Neural Radiance Fields](https://arxiv.org/abs/2304.06706) - 虽与本文同期发表，但代表了基于网格的 NeRF 方法的巅峰，极具对比价值。
