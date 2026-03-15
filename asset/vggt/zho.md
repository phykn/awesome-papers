# VGGT: Visual Geometry Grounded Transformer

- **Authors**: Jianyuan Wang, Minghao Chen, Nikita Karaev, Andrea Vedaldi, Christian Rupprecht, David Novotny
- **Venue/Date**: CVPR 2025 (Best Paper Award) / arXiv 2025年3月
- **URL**: [https://arxiv.org/abs/2503.11651](https://arxiv.org/abs/2503.11651)
- **GitHub**: [https://github.com/facebookresearch/vggt](https://github.com/facebookresearch/vggt)

---

### 1. 背景

传统的三维重建工作长期以来依赖于诸如运动恢复结构 (**SfM**) 和捆绑调整 (**BA**) 等视觉几何方法，这些方法依赖于复杂的迭代优化，处理速度较慢。虽然最近的 DUSt3R 和 MASt3R 等深度学习模型已转向“几何优先”架构，但它们通常受限于特定任务（如双视图匹配），或者仍需昂贵的全局对齐步骤来生成连贯的场景。开发一个统一、快速且“即插即用”、能够处理从单张到数百张图像的系统一直是一个挑战。

### 2. 直觉

想象一下，你正试图从一堆散乱的宝丽来照片中重建一座大楼。你首先会观察每张照片以识别局部形状和深度（**帧内注意力**(Frame-wise Attention)），然后将它们全部平铺在桌面上，移动位置以查看它们的边界如何在 3D 空间中重叠和对齐（**全局注意力**(Global Attention)）。VGGT 正是执行这种“大脑体操”：它在完善每张照片内部的“局部” 3D 细节与维持所有可用视角之间的“全局”一致性之间不断切换。

### 3. 重大突破

VGGT 的核心洞察在于 **交替注意力**(Alternating-Attention) Transformer。该模型并非使用单一的注意力块，而是有意在单帧内的自注意力和所有帧之间的全局注意力之间交替。这一简单而深刻的架构选择使得单一的前馈网络能够执行以前需要多个专用模型才能完成的任务——在不到一秒的时间内同时估计相机姿态、深度图、稠密点云，甚至跨时间跟踪 3D 点。

### 4. 技术机制

#### 4.1 流水线

![Pipeline Figure](figures/fig01_pipeline.png)

- 输入图像通过预训练的 DINO 骨干网络转换为 Patch（补丁）。这些 Patch 辅以“相机标记”(Camera Tokens)，通过交替注意力层来解析 3D 几何结构。
- (1) 模型同时预测相机、点图、深度图和点轨迹。(2) 它在单次前馈过程中即可处理任意数量的图像。

#### 4.2 架构 / 核心设计

![Architecture Figure](figures/fig02_architecture.png)

- VGGT 为每一帧的标记添加特定的“相机标记”来表示其 3D 状态。专用头——用于密集图预测的 **DPT**(Dense Prediction Transformer) 和用于相机的线性头——负责解码 Transformer 最终的特征表示。
- (1) 该架构使用 24 层交替注意力来平衡局部细节和全局上下文。(2) 通过使用唯一的、可学习的参考标记，将第一帧视为世界坐标系的参考。

#### 4.3 核心公式

该模型使用结合了相机、深度和点图监督以及**等方差不确定性**(aleatoric uncertainty) ($\Sigma$) 的多任务损失进行训练。例如，深度损失结合了直接值差异和用于保持边缘锐度的梯度项：

$$ \mathcal{L}\_{\text{depth}} = \sum_{i=1}^N \left( \Vert \Sigma\_i^D \odot (\hat{D}\_i - D\_i) \Vert + \Vert \Sigma\_i^D \odot (\nabla \hat{D}\_i - \nabla D\_i) \Vert - \alpha \log \Sigma\_i^D \right) $$

- $D\_i$: 第 $i$ 帧的地面真值深度 (Sec 3.4)。
- $\hat{D}\_i$: DPT 头输出的预测深度图 (Sec 3.3)。
- $\Sigma\_i^D$: 预测的不确定性图，根据置信度对损失进行加权 (Sec 3.4)。
- $\nabla$: 梯度算子，确保预测的深度图保留锐利的物体边界 (Sec 3.4)。


#### 4.4 比较：其他方法 vs 本论文（基于证据）

VGGT 为前馈式 3D 重建设立了效率和准确性的新标准。虽然像 MASt3R 这样的里程碑式方法由于昂贵的迭代全局对齐而每场景需要约 9-10 秒，但 VGGT 在纯前馈模式下仅需 0.2 秒即可获得更优的结果 (Table 3)。其最大的特色在于统一的交替注意力 Transformer，它消除了对特定任务“侧向模型”或三角测量的需求。在 RealEstate10K 基准测试中，尽管未在该数据集上进行训练，它的 AUC@30 指标仍比最强的基准模型高出 10% 以上 (Table 1)。论文也提到了一项权衡：虽然前馈结果已达最前沿水平，但通过引入捆绑调整 (BA) 可以进一步提高精度，代价是轻微的延迟增加 (Sec 4.1)。

#### 4.5 定性结果

![Qualitative Results](figures/fig03_qualitative.png)

与 DUSt3R 等优化方法相比，VGGT 展示了卓越的鲁棒性。根据图 3 的描述：在第一行中，该模型准确地恢复了油画的几何结构，而 DUSt3R 产生了一个扭曲的平面。在具有挑战性的“无重叠”案例中（第二行），VGGT 仍然恢复了场景结构，而 DUSt3R 则完全失败。第三行显示，即使在具有重复纹理的情况下，VGGT 也能保持高质量的几何形状。与 DUSt3R 在超过 32 帧时会因显存 (VRAM) 不足而崩溃不同，VGGT 的高效内存扩展允许它稳定地处理更大规模的场景。

### 5. 影响

VGGT 成功挑战了“准确的 3D 重建必须依靠迭代优化”这一假设。通过证明设计良好的 Transformer 可以仅凭简单的单次前馈学习多视图几何，它将姿态、深度、点云、轨迹等多种视觉任务整合到了一个可扩展的单一骨干网络中。这极大地简化了实时机器人、AR/VR 和自动驾驶领域的现有流水线。

### 6. 延伸阅读

- [VGGT-X: When VGGT Meets Dense Novel View Synthesis](https://arxiv.org/abs/2509.25191) 这一后续工作将 VGGT 扩展到 1,000 多张图像，并针对高斯泼溅 (Gaussian Splatting) 进行了优化。
- [MASt3R-SLAM: Real-Time Dense SLAM with 3D Reconstruction Priors](https://arxiv.org/abs/2412.12392) 利用 3D 重建先验在各种相机模型中实现实时稠密 SLAM。
- [Pow3R: Empowering Unconstrained 3D Reconstruction with Camera and Scene Priors](https://arxiv.org/abs/2503.17316) 用于广泛回归任务的多模态 3D 基础模型。
- [GaussTR: Foundation Model-Aligned Gaussian Transformer for Self-Supervised 3D Spatial Understanding](https://arxiv.org/abs/2412.13193) 将 3D 高斯表示直接集成到 Transformer 架构中，以实现体积感知。
