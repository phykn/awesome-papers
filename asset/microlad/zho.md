# MicroLad: Latent Diffusion-Based 2D-to-3D Microstructure Reconstruction with Inverse Design

- **作者**: Kang-Hyun Lee, Gun Jin Yun
- **会议/日期**: Preprint (2025)
- **URL**: [https://github.com/KangHyunL/microlad](https://github.com/KangHyunL/microlad)
- **GitHub**: [https://github.com/KangHyunL/microlad](https://github.com/KangHyunL/microlad)

---

### 1. 背景
获取具有代表性的 3D 微观结构数据集对于集成计算材料工程 (ICME) 至关重要，但由于 X 射线 CT 或连续切片法等实验成本高昂，这仍然非常困难。虽然 2D 微观组织照片相对容易获得，但传统的 2D 到 3D 重建方法存在根本局限性。基于描述符 (descriptor) 的方法受限于所选描述符的信息量，不同的微观结构可能共享几乎相同的统计数据。基于数据的方法（如 SliceGAN 或多平面去噪扩散，MPDD）可以重建统计学上等效的 3D 体积，但无法生成*超出*训练分布的微观结构，从而限制了设计空间的探索。因此，需要一个既能实现忠实重建，又能针对目标特性进行逆向设计 (inverse design) 的框架。

### 2. 直觉
想象一下，仅凭一张材料的 2D 截面照片，你想构建一个完整的 3D 模型，该模型不仅在任何角度看起来都真实，而且还能达到特定的目标性能（例如最大扩散率）。MicroLad 的工作方式就像一位已经学会了如何从任何方向雕刻真实截面的雕刻家（预训练的 2D 潜在扩散模型）。这位雕刻家通过检查三个正交方向的一致性来组装 3D 块。核心区别在于额外的“指导信号” (Score Distillation Sampling)，它将每个截面微调向所需的物理特性方向。这就好比一位教练引导画家不仅要画出真实的纹理，还要安排最终结构以最优化导热。

### 3. 突破
MicroLad 的决定性见解在于将**基于潜在扩散 (Latent Diffusion) 的 2D 到 3D 重建**与**结合分数蒸馏采样 (Score Distillation Sampling, SDS) 的逆向设计**相结合。以前的扩散方法虽然可以重建 3D 微观结构，但局限于训练分布的再现。MicroLad 在预训练 VAE 学习到的潜在空间中运行，通过多平面扩散确保 3D 一致性，然后应用 SDS 引导生成朝着用户指定的目标——微观结构描述符（体积分数、表面积）或有效物性（扩散率）方向进行。在整个过程中不需要重新训练扩散模型。

### 4. 技术机制

#### 4.1 流水线
![Pipeline Figure](figures/fig01_pipeline.png)
- (1) 该图展示了 MicroLad 的完整流水线：(a) 获取 2D 微观结构数据，(b) 通过 VAE 进行潜在空间编码，(c) 训练潜在扩散模型，(d) 通过潜在多平面去噪扩散 (L-MPDD) 进行 2D 到 3D 重建，(e) 基于 SDS 的逆向控制。(2) 核心设计选择是在压缩的潜在空间 (4×16×16) 而非像素空间中执行所有扩散运算，从而大幅降低了计算成本。

#### 4.2 架构 (Architecture)
![Comparison Figure](figures/fig02_comparison.png)
- (1) 该图对比了传统的计算材料工程工作流（仅支持正向 SP 连接）与支持正向和逆向 SP 连接的 MicroLad 方法。(2) 核心创新在于闭环：不仅能从结构预测性能，还能通过潜在空间中的 SDS 优化，生成以特定性能为目标的结构。

#### 4.3 核心公式
- **公式**: 

$$ \mathcal{L}\_{\text{SDS}} = \kappa(t) \Vert \epsilon - \epsilon\_\theta(z\_{\text{slice},t}, t) \Vert^2, \text{ 其中 } \kappa(t) = \frac{1 - \bar{\alpha}\_t}{\bar{\alpha}\_t} $$

- SDS 损失用于衡量当前潜在截面与冻结的扩散模型所学习到的分布的拟合程度。它与描述符匹配损失 ($\mathcal{L}\_M = \Vert M(\hat{x}\_{\text{slice}}) - M^{\ast} \Vert^2$) 以及物性损失 ($\mathcal{L}\_P = \Vert H(\hat{x}\_{\text{slice}}) - P^{\ast} \Vert^2$) 相结合，使总梯度引导潜在表示朝着既真实又具有所需目标物性的微观结构方向演变。
- **变量**:
  - $\epsilon\_\theta$: 提供扩散先验信息的冻结的预训练去噪网络 (U-Net) (第 3.4 节 / 式 39)。
  - $z\_{\text{slice}}$: 由 VAE 编码器 $E$ 编码得到的 2D 截面的潜在表示 (第 3.4 节 / 式 37)。
  - $M^{\ast}, P^{\ast}$: 用户指定的目标微观结构描述符和有效物性 (第 3.4 节 / 式 42-43)。
  - $H$: 用于计算有效扩散率的可微分物理求解器 (FEM) (第 3.4 节 / 式 43)。

#### 4.4 比较：其他技术 vs 本文
MicroLad 大幅扩展了现有基于扩散的微观结构重建方法的能力。虽然 MPDD (Micro3Diff) 可以重建与 2D 训练数据统计等效的 3D 体积，但无法生成具有受控目标物性的微观结构。基于 GAN 的方法 SliceGAN 存在众所周知的模式崩坏 (mode collapse) 问题，且无法进行性能导向的生成。MicroLad 在潜在空间中运行（4×16×16 对比全分辨率），既保持了忠实度又降低了计算成本。重建的二相及三相微观结构的二点相关函数 ($S_2$) 误差率始终低于 5% (第 4.1 节 / 图 3-4)。决定性的是，MicroLad 成功实现了针对体积分数、表面积和相对扩散率目标的逆控制生成 (第 4.2 节 / 图 5-7)。不过，物性导向的生成需要可微分的物理求解器，因此其应用局限于可以被高效求导的物性 (第 3.4 节)。

#### 4.5 定性结果
![Qualitative Results - Binary](figures/fig03_qualitative.png)
二相碳酸盐微观结构的定性结果显示，MicroLad 忠实地重建了 3D 体积，其截面与原始 2D 训练图像在视觉上无法区分。二点相关函数 ($S_2$) 和线性路径函数 ($L_2$) 在三个正交方向上都显示出生成样本与原始样本之间极佳的一致性 (图 3d)。重建的 3D 体积展示了真实碳酸盐微观结构所特有的真实孔隙连通性和空间异质性。

![Qualitative Results - Three Phase](figures/fig04_qualitative_threephase.png)
在三相 SOFC（固体氧化物燃料电池）微观结构的情况下，MicroLad 成功捕获了孔隙相、离子导电相和电子导电相各自独特的形态，同时保持了它们之间的空间相互关系。所有三相的 $S_2$ 和 $L_2$ 函数都与原始样本密切吻合，证实了形态忠实度 (图 4d)。考虑到必须保持物理上一致的相边界的多相结构的复杂性，这一点尤为引人注目。

### 5. 影响
MicroLad 代表了在闭合微观结构表征与材料设计之间闭环方向上的重要进展。通过将潜在扩散模型与分数蒸馏采样及可微分物理求解器相结合，它使研究人员不仅能够从 2D 观察中重建真实的 3D 微观结构，还能针对特定的材料物性对微观结构进行逆向设计。这种能力可以直接用于加速能源材料（SOFC、电池）、结构复合材料等 3D 微观结构决定性能的系统的 ICME 工作流。

### 6. 后续研究
[1] [Multi-plane denoising diffusion-based dimensionality expansion (Micro3Diff)](https://doi.org/10.1038/s41524-024-01280-z)<br>
同一作者先前的框架，奠定了 2D 到 3D 重建的多平面扩散基础。<br>
[2] [Score Distillation Sampling (DreamFusion) (2022)](https://arxiv.org/abs/2209.14988)<br>
将 2D 扩散模型的知识蒸馏到 3D 表示中的基础技术。<br>
[3] [SliceGAN: 通过基于 GAN 的维度扩展从 2D 切片生成 3D 结构 (2021)](https://arxiv.org/abs/2102.07708)<br>
2D 到 3D 微观结构生成的基于 GAN 的基准。<br>
[4] [Latent Diffusion Models (Stable Diffusion) (2021)](https://arxiv.org/abs/2112.10752)<br>
MicroLad 所基于的核心潜在扩散架构。<br>
