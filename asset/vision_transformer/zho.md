# An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale
- **Authors**: Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, Jakob Uszkoreit, Neil Houlsby
- **Venue/Date**: ICLR 2021
- **URL**: https://arxiv.org/abs/2010.11929
- **GitHub**: https://github.com/google-research/vision_transformer

### 1. 背景
- 从图像中提取特征的传统方法严重依赖卷积神经网络 (CNN)，这种方法由于其感受野是局部的，很难捕捉长距离的全局相关性。
- 尽管 Transformer 在自然语言处理领域带来了革命性的变化，但在图像的像素级别直接应用它们计算代价极其高昂。这篇论文通过将图像分块成为互不重叠的“斑块 (patches)”，证明了纯 Transformer 可以超越当时最主流 CNN 的极佳性能。

### 2. 直观理解
- 想象你正在阅读一本图画书。与其像 CNN 那样用一个小放大镜逐行逐点去扫描，不如干脆把这幅画精确裁剪成网格状的一堆识字卡片。
- **Vision Transformer** (ViT) 把这些 16x16 尺寸的图块当作句子里的“单词”。这么做赋予了模型能力去立刻建立在这个图像里任意两点之间微小细节的普遍关联。

### 3. 核心突破
- 这里顿悟般的洞察在于彻底抛弃卷积操作。通过让这些没有重叠的视觉区块展平为普通的线性向量，并配合位置标签输入给标准 NLP Transformer 处理，让它在无需人为设定的视觉归纳偏置下学会捕捉广泛的全局连接网络。

### 4. 技术机制

#### 4.1 处理管线 (Pipeline)
![Pipeline Figure](figures/fig01_pipeline.png)
- 原始图像被分解成固定尺寸的斑块并进行了线性映射并标记位置信息，然后与一个专门用于分类的标记一起输入给标准的 Transformer 编码器。
- 它展示了什么：图像经由这些斑块组成的特征实现端对端的运算。
- 核心变量：处于最顶层网络输出状态下的 `[class]` 标签代理直接决定了最后的图像预测。

#### 4.2 架构与核心设计 (Architecture / Core Design)
![Architecture Figure](figures/fig01_pipeline.png)
- 它的内部结构极其遵从最为标准的自然语言 Transformer 编码器体系框架，通过交替堆叠多头自注意力层网络与多层感知机块模块组成。
- 它展示了什么：在不同 Transformer 网络内部层中的信息数据流规范化处理。
- 核心设计选择：ViT 完全依靠自注意力机制操作，剔除了任何类似于平移不变性与局部优先原则等先天的视觉预设偏好，从而迫使它只有纯粹建立于大规模数据去学习并重构局部的结构布局。

#### 4.3 核心方程 (Core Equation)
- 核心的自注意力机制负责找到在全图小块之中的深层隐秘关联：

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

- $Q$: 代表要寻找相关视觉线索块面的查询矩阵 (Sec 3.1)。
- $K$: 提供特征来去应对各类相关块匹配要求的键矩阵。
- $V$: 从中萃取出并汇整具体视觉结果信息的值矩阵。
- $d_k$: 用于对点积的值进行缩放并且让梯度的更新计算得以保持平稳状况的维度。

#### 4.4 比较：现有模型 vs 本研究 (Comparison)
- 作者表明只要能给予非常丰沛海量的训练数据集环境，纯粹的 Transformer 便会战胜拥有大量技巧的顶级卷积网络。以 ResNet 等标准构架作参照，它们欠缺早期阶段全方位的接纳感知范围，从而限制了综合解析能力的完整展现能力。相反，ViT 不利用丝毫传统视域定制化操作运算直接执行自我注意力。这项机制允许模型打从极低层结构（如 Fig 11 所示）长线捕获相距甚远的相互依赖状况影响。缺点表现则是，ViT 在很大程度上必须倚赖诸如 JFT-300M 体量巨型的库数据，用以补全放弃掉那些先天对于像素位置极度友好的规则设置条件约束。

#### 4.5 定性结果验证 (Qualitative Results)
![Qualitative Results](figures/fig06_qualitative.png)
- 当从最末的特征端追溯关注热力图落点时反馈呈现情况揭露，ViT 对原本没有经过特别教导过的物体内里显著目标自发式地表现出惊人的灵敏区锁定反馈力。
- 虽然没存在特有的空域规定法则，该架构下的各大运算视线仍不偏不倚紧凑包围指向主干客体要素并且对杂乱细碎无意义的其余景物进行了极为卓越而彻底忽略回避的操作。

### 5. 研究影响力 (Impact)
- ViT 凭一己之力让计算机视觉发生了颠覆性的转变从而论证了想要进行图像的最优质识别并不一定需要包含繁杂深厚的常规卷积模型基座。这起到了统合并确立未来自然文本处理以及机器视觉等各个主要版图间无缝交互标准模型的深远价值作用。

### 6. 深入阅读文献 (Further Reading)
[1] [Attention Is All You Need (2017)](https://arxiv.org/abs/1706.03762)<br>
介绍了最初始的 Transformer 网络基础理论与设计的开元巨著。<br>
[2] [Training data-efficient image transformers & distillation through attention (2020)](https://arxiv.org/abs/2012.12877)<br>
提出了新颖途径可以无需使用极其大体量的背景数据前提实现保障高效稳妥训练运转目标。<br>
[3] [Swin Transformer: Hierarchical Vision Transformer using Shifted Windows (2021)](https://arxiv.org/abs/2103.14030)<br>
把自注意力置于偏移式的局部格窗中实施有效演练衍生具备层级架构进而表现出高算力的扩张形式。<br>
