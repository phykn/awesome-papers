# Multi-plane denoising diffusion-based dimensionality expansion for 2D-to-3D reconstruction of microstructures with harmonized sampling

- **作者**: Kang-Hyun Lee, Gun Jin Yun
- **会议/日期**: npj Computational Materials (2024)
- **URL**: [https://doi.org/10.1038/s41524-024-01280-z](https://doi.org/10.1038/s41524-024-01280-z)
- **GitHub**: 论文中未注明。

---

### 1. 背景
表征 3D 微观结构对于理解材料特性至关重要，但通过 X 射线 CT 或连续切片法 (serial sectioning) 等手段获取 3D 数据集的成本和时间非常高。相比之下，2D 微观组织照片 (micrographs) 丰富且易于获取。现有的 2D 到 3D 重建方法大多依赖大量的 3D 训练数据，或者难以在三维空间中保持空间连通性和物理真实性。因此，急需一种无需昂贵的 3D 数据就能将 2D 知识扩展到 3D 的新框架。

### 2. 直觉
核心直觉是：“如果是一个有效的 3D 结构，无论从哪个正交方向（XY, YZ, ZX 平面）切割，它看起来都应该像真实的 2D 图像。”我们可以把这想象成雕塑家创作 3D 作品的过程。通过不断从正面、侧面和上方检查并打磨形状，最终完成一个整体一致的形态。Micro3Diff 应用这一原理，使用预训练的 2D 扩散模型 (Diffusion Model) 同时对三个方向的所有截面进行“去噪 (denoising)”或“打磨”，从而强制它们和谐地合并成一个连通的 3D 体积。

### 3. 突破
本论文的决定性见解 (Aha! insight) 是：**维度扩展 (dimensionality expansion) 是在推理（采样）阶段而非学习阶段完成的**。这意味着可以直接利用现有已构建的高质量 2D 扩散生成模型 (DGM)，只需在生成过程中赋予其 3D 一致性即可。结果是完全不需要任何 3D 训练数据，使得材料科学家们能够非常灵活、高效地使用该框架。

### 4. 技术机制

#### 4.1 工作流
![Pipeline Figure](figures/fig13_pipeline.png)
- (1) 该示意图展示了含噪声的 3D 体积如何被分解为三个正交平面（YZ、XZ、XY）。(2) 这些切片使用预训练的 2D 扩散模型进行迭代去噪，通过交界处的信息重叠隐式强制实现 3D 连通性。

#### 4.2 架构 / 核心设计
![Architecture Figure](figures/fig16_algorithm.png)
- (1) 该图描绘了**协调采样**（Harmonized Sampling）循环，旨在解决因定期切换去噪平面而导致的“不协调”问题。(2) 每个时间步包含去噪和随后的“再加噪”（重新添加少量高斯噪声）循环，以迫使 3D 体积稳定在更符合物理一致性的轨迹上。

#### 4.3 核心公式
- **公式**:

$$ x_{t-1} = \mathcal{G}\left( \bigcup_{p \in \{XY, YZ, ZX\}} \epsilon_\theta(\text{Slice}_p(x_t), \sigma_t) \right) $$

- 核心逻辑是多平面去噪，其中步骤 $t$ 的 3D 体积 $x$ 通过汇总（函数 $\mathcal{G}$）来自应用于三个正交方向切片的 2D 去噪网络 $\epsilon_\theta$ 的信息进行更新。为了确保稳定性，在反向扩散过程中会多次（$n_h$ 次协调步）应用再加噪步骤 $p(x'_t | x_{t-1}) = \mathcal{N}(x'_t; \sqrt{1-\beta_t} x_{t-1}, \beta_t I)$。

- **变量**:
  - $x_t$: 扩散时间步 $t$ 的 3D 微观结构体素（第 4.1 节）。
  - $\epsilon_\theta$: 在所有平面共享的预训练 2D 去噪生成模型 (U-Net)（第 4.2 节）。
  - $n_h$: 用于弥合正交去噪平面之间差距的协调（重采样）步数（图 16）。


#### 4.4 比较：其他技术 vs 本论文
相比于标准的逐切片生成，Micro3Diff 展示了优异的 3D 连通性和形态学准确性。传统的 2D 方法缺乏面外（out-of-plane）一致性，而 Micro3Diff 确保了二点相关函数 ($S\_2$) 和线性路径函数 ($L\_2$) 在所有方向上统计等效（第 3 节 / 图 4）。与朴素的多平面方法相比，协调采样过程显著降低了捕捉复杂特征（如多晶晶界）的误差率（图 5）。一个明显的权衡是，由于采用了三平面去噪循环，每个 3D 体积的计算时间有所增加（第 3.1 节）。

#### 4.5 定性结果
![Qualitative Results](figures/fig02_qualitative.png)
定性结果（图 2）展示了协调步数 ($n_h$) 如何直接影响重构球形夹杂物的物理真实性。当 $n_h=0$ 时，结构出现明显的伪影且切片间连通性较差；而 $n_h=10$ 则产生了平滑的球形边界，与训练分布完美匹配。该框架还成功重构了复杂的多相系统，如多晶颗粒（图 7）和 NMC 电池正极（图 9），在从未见过真实 3D 训练样本的情况下，保持了真实的节点几何形状和扭曲度。

### 5. 影响
Micro3Diff 为材料信息学（Materials Informatics）提供了强大的工具，使研究人员能够从易于获取的 2D 数据中生成高保真 3D 微观结构。这显著降低了进行高通量模拟和集成计算材料工程（ICME）的门槛，有效弥补了简易 2D 获取与必要 3D 表征之间的差距。

### 6. 延伸阅读
[1] [MicroLad: 2D-to-3D Microstructure Reconstruction and Generation via Latent Diffusion and Score Distillation (2025)](https://arxiv.org/abs/2502.10052)<br>
一个直接的后续研究，将过程移至潜在空间，以实现更快、更受控的 3D 生成。

[2] [Exascale granular microstructure reconstruction in 3D volumes of arbitrary geometries with generative learning](https://doi.org/10.1016/j.cma.2025.117764)<br>
探索将这些生成方法扩展到大规模体积和复杂边界条件。

[3] [GrainPaint: A multi-scale diffusion-based generative model for microstructure reconstruction of large-scale objects](https://doi.org/10.1016/j.actamat.2025.120815)<br>
专注于基于修复（inpainting）的扩散，以重构大规模多晶材料。
