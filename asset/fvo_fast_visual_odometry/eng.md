# FVO: Fast Visual Odometry with Transformers

- **Authors**: Vladimir Yugay, Duy-Kien Nguyen, Theo Gevers, Cees G. M. Snoek, Martin R. Oswald
- **Venue/Date**: arXiv 2026 (Published: March 9, 2026) / ICLR 2026 (Pre-print)
- **URL**: [https://arxiv.org/abs/2510.03348](https://arxiv.org/abs/2510.03348)
- **GitHub**: [https://vladimiryugay.github.io/fvo](https://vladimiryugay.github.io/fvo)

---

### 1. Background

Traditional monocular visual odometry (VO) systems are typically built as hybrid pipelines that combine deep neural networks for feature extraction with classical geometric optimization, such as **bundle adjustment** (BA). While accurate, these methods face two major bottlenecks: they are computationally expensive due to iterative optimization, and they often struggle to estimate absolute metric scale without extrinsic calibration. Recently, large 3D models like DUSt3R have shown promise in geometric understanding but are too slow or lack the temporal consistency required for continuous video streams. There is a critical need for a VO system that is both end-to-end and fast enough for real-time applications.

### 2. Intuition

Imagine you are walking through a crowded train station. To figure out where you are going, you don't build a perfect 3D map of every brick and person; instead, you instinctively sense your relative motion by watching how the scenery shifts from moment to moment. Crucially, you also know when to trust your eyes—if you're walking past a plain white wall, you realize your sense of motion is less reliable and you rely on other cues. FVO works exactly like this "Intuitive Navigator." It replaces rigid geometric math with a transformer that directly "feels" the relative motion between frames while simultaneously learning to predict its own uncertainty.

### 3. Breakthrough

The definitive insight of FVO is the formulation of visual odometry as a direct **relative pose regression** problem with learned **heteroscedastic uncertainty**. Instead of treating VO as a reconstruction-and-optimization task, FVO uses a high-capacity transformer to map overlapping image windows directly to camera trajectories. The "Aha!" moment comes from the **confidence-aware inference scheme**: by predicting how certain it is about each relative pose, the model can robustly aggregate hundreds of overlapping predictions into a smooth global trajectory, effectively replacing the need for expensive bundle adjustment with a simple, weighted averaging process.

### 4. Technical Mechanism

#### 4.1 Pipeline

![Pipeline Figure](figures/fig01_pipeline.png)

- FVO processes short, overlapping video windows through an efficient transformer to estimate relative poses and confidence scores. These local estimates are then fused by an inference module into a consistent metric trajectory.
- (1) The figure shows the transition from raw video frames to a unified metric camera trajectory. (2) Overlapping windows allow the model to refine its estimates through redundancy and confidence weighting.

#### 4.2 Architecture / Core Design

![Architecture Figure](figures/fig02_architecture.png)

- The architecture consists of a frozen pre-trained encoder (from CroCo/DUSt3R) followed by a **Time-Space Decoder** with repeating temporal and spatial attention blocks. It uses learnable camera tokens to aggregate information across the sequence.
- (1) The figure illustrates the flow from per-image token embeddings to final pose and confidence heads. (2) Predicting rotations on the $SO(3)$ manifold ensures that all relative rotations remain mathematically valid.

#### 4.3 Core Equation

The network is trained using a **Confidence-Aware Loss** function that integrates learnable uncertainty parameters $c\_R, c\_t$ for both rotation and translation. This allows the model to "self-calibrate" by down-weighting residuals it identifies as noisy or unreliable.


$$ \mathcal{L} = \mathcal{L}\_{\text{rot}} \exp(-c\_R) + c\_R + \mathcal{L}\_{\text{trans}} \exp(-c\_t) + c\_t $$

- $\mathcal{L}\_{\text{rot}}$: Geodesic loss between predicted and ground-truth rotation matrices (Eq 9).
- $\mathcal{L}\_{\text{trans}}$: $L1$ loss between predicted and ground-truth relative translations (Eq 10).
- $c\_R, c\_t$: Learned log-variance parameters representing uncertainty for rotation and translation, respectively (Sec 3.3).
- $\exp(-c)$: The precision term that automatically weights the importance of the error based on predicted confidence (Sec 3.3).


#### 4.4 Comparison: Others vs This Paper (Evidence-Based)

FVO represents a significant leap in VO efficiency without sacrificing accuracy. While strong baselines like DPVO rely on complex bundle adjustment loops that limit speed to roughly 35 FPS, FVO achieves nearly 76 FPS—a 2x speedup—on the same hardware (Table 1). Unlike large-scale models such as VGGT or MASt3R-SLAM, which struggle with scale ambiguity or memory limits on long sequences, FVO maintains robust metric trajectories by utilizing its confidence-aware aggregation (Sec 4.1). Evidence from the ScanNet and ARKit benchmarks shows that FVO outperforms all non-optimization baselines in Absolute Trajectory Error (ATE) while remaining competitive with the best hybrid methods (Table 1). The only stated trade-off is its focus on static environments; its performance in highly dynamic scenes remains a future research direction (Sec 5).

#### 4.5 Qualitative Results

![Qualitative Results](figures/fig07_qualitative.png)

The qualitative trajectory results on ScanNet and ARKit demonstrate FVO's superior robustness compared to existing end-to-end models. As seen in Figure 7, FVO (shown in blue/cyan) closely tracks the ground truth trajectories (dashed lines) across complex circular and linear motions, where earlier models like TSFormer and CUT3R exhibit significant drift or total failure. Notably, FVO manages to maintain absolute scale across different sequences without any manual per-dataset tuning. The color-coding reveals that FVO keeps the ATE RMSE consistently low (mostly in the blue range), whereas baselines often spike into high-error red zones during sharp turns or low-texture segments. A minor limitation is visible in extremely long-range trajectories where a slight cumulative drift can still be observed (Fig 7, bottom row).

### 5. Impact

FVO paves the way for a new generation of purely learning-based SLAM systems that are fast, robust, and calibration-free. By proving that a well-designed transformer can replace classic geometric optimization blocks, it removes a major barrier to deploying high-performance VO on low-power mobile devices and robots. Its end-to-end nature simplifies the engineering stack, making it easier to integrate visual odometry into broader multi-modal intelligence systems for autonomous navigation and augmented reality.

### 6. Further Reading

- [LEVIO: Lightweight Embedded Visual Inertial Odometry for Resource-Constrained Devices](https://arxiv.org/abs/2602.03294) A highly optimized VIO pipeline that targets ultra-low-power embedded platforms, pushing the boundaries of efficiency.
- [OpenVO: Open-World Visual Odometry with Temporal Dynamics Awareness](https://arxiv.org/abs/2602.19035) Explores visual odometry in uncalibrated, open-world settings like dashcam footage using temporal encoding.
- [MDE-VIO: Enhancing Visual-Inertial Odometry Using Learned Depth Priors](https://arxiv.org/abs/2602.11323) Integates deep-learned depth priors into traditional VIO backends to improve robustness in low-texture environments.
