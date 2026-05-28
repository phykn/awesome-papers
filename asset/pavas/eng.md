# PAVAS: Physics-Aware Video-to-Audio Synthesis

- **Authors**: Oh Hyun-Bin, Yuhta Takida, Toshimitsu Uesaka, Tae-Hyun Oh, Yuki Mitsufuji
- **Venue/Date**: CVPR 2026 (Oral) / arXiv revised March 30, 2026
- **URL**: [https://arxiv.org/abs/2512.08282](https://arxiv.org/abs/2512.08282)
- **GitHub**: Not released yet; project page lists code as coming soon.

---

### 1. Background

Video-to-audio generation has become good at the obvious parts: if a video shows a dog barking, a drum hit, or a hammer strike, modern models can often produce audio with roughly the right semantic label and timing. The weakness is that these systems usually learn visual-audio correlations rather than the physical cause of the sound. A hammer and a light plastic toy can both appear as "an object hitting something," but their mass, speed, and impact energy should change the loudness, decay, and spectral sharpness of the sound. PAVAS is necessary because visually plausible audio is not always physically plausible audio: the sound should not only match what happened, but also how strongly it happened.

### 2. Intuition

Imagine watching a video with the sound muted while trying to Foley it by hand. A beginner might label the scene as "hammering" and paste in a generic clang. A skilled Foley artist watches the swing: how heavy the tool looks, how fast it moves, whether the impact is sharp or weak, and how the object rebounds. PAVAS tries to give a video-to-audio model that second kind of judgment. Instead of asking only "what object is visible?", it asks "what physical event is this object undergoing?" and uses mass and velocity as compact clues about the energy that should become sound.

### 3. Breakthrough

The key insight is to inject explicit object-level physics into a latent diffusion video-to-audio model without requiring supervised audio-physics labels. PAVAS first estimates physical parameters from ordinary monocular video: a Vision-Language Model estimates the moving object's mass, while segmentation plus dynamic 3D reconstruction recovers object trajectories for velocity. Then the Physics-Driven Audio Adapter (Phy-Adapter) turns those scalar physics cues into conditioning signals for the diffusion transformer. The "Aha!" is that physics is not treated as a separate simulator; it becomes a residual modulation signal that nudges the generative audio trajectory toward sounds whose acoustic strength follows the video's physical dynamics.

### 4. Technical Mechanism

#### 4.1 Pipeline

![Pipeline Figure](figures/fig02_pipeline.png)

- The figure shows PAVAS from silent video to generated audio: PPE extracts moving-object mass and velocity, Phy-Adapter fuses those cues with object-centric visual features, and the diffusion transformer generates audio latents under video, text, audio, and physics conditions.
- The important variables are $m\_i$ for each object's mass and $v\_i^\ell$ for its per-frame velocity; these become $c\_{\text{mass}}$ and $c\_{\text{vel}}$, the physics conditions injected into the model.

#### 4.2 Architecture / Core Design

- Pseudo-figure flow: video frames -> moving-object discovery -> masks and 3D point clouds -> mass/velocity estimates -> object-centric visual features -> FiLM modulation -> residual physics modulation inside diffusion transformer blocks.
- The core design choice is residual $\Delta$-modulation: physics cues adjust AdaLN parameters through zero-initialized gated MLPs, so the pretrained multimodal diffusion path is refined by physics rather than overwritten by raw scalar inputs.

#### 4.3 Core Equation

The core equation is the $\Delta$-modulation rule used by Phy-Adapter. It keeps the original multimodal AdaLN modulation and adds learned residual corrections from mass and velocity conditions.

$$ \tilde{\omega} = \omega(\mathbf{c}\_{\text{multi}}) + \alpha\_m g\_m(\mathbf{c}\_{\text{mass}}) + \alpha\_v g\_v(\mathbf{c}\_{\text{vel}}) $$

- $\tilde{\omega}$: physics-augmented AdaLN modulation parameters used inside each diffusion transformer block (Eq 10).
- $\omega(\mathbf{c}\_{\text{multi}})$: original AdaLN scale and shift parameters from multimodal video, text, audio, and timestep conditions (Sec 3.4).
- $\mathbf{c}\_{\text{mass}}$: aggregated mass condition created from PPE mass estimates and object-centric visual features (Sec 3.4).
- $\mathbf{c}\_{\text{vel}}$: aggregated velocity condition created from PPE velocity sequences and object-centric visual features (Sec 3.4).
- $g\_m, g\_v$: lightweight zero-initialized MLPs that transform the physics conditions into residual modulation terms (Eq 10).
- $\alpha\_m, \alpha\_v$: learnable gates controlling how strongly mass and velocity affect the diffusion block (Eq 10).

#### 4.4 Comparison: Others vs This Paper

Existing V2A systems such as See & Hear, V-AURA, VATT, TARO, FoleyCrafter, and MMAudio can produce semantically relevant and temporally synchronized audio, but PAVAS argues that they still miss the coupling between physical magnitude and acoustic response. The paper's VGG-Impact analysis shows APCC-∆ values above 0.5 for many baselines, while PAVAS-L reaches the lowest APCC-∆ at 0.378, closer to the ground-truth audio-physics relationship (Table 1). Compared with MMAudio-L, the direct backbone predecessor, PAVAS-L improves distribution metrics such as $FD\_{\text{PaSST}}$ from 60.60 to 47.38 and IB-score from 33.22 to 35.41 while keeping DeSync nearly unchanged (Table 1). The mechanism behind the gain is not just longer training: Table 3 reports that adding mass or velocity helps, combining both helps most, and residual $\Delta$-modulation beats direct summation. The trade-off is engineering complexity, since PAVAS depends on several pretrained vision components and currently focuses on physical factors such as mass and velocity rather than richer material modeling (Sec 5).

#### 4.5 Qualitative Results

![Qualitative Results](figures/fig03_qualitative.png)

Figure 3 compares spectrograms from several V2A baselines against PAVAS and ground truth. In the trampoline example, visual event markers line up with sharper spectral changes in the PAVAS row than in many baselines, which either blur events or place strong components away from the marked impacts. In the tuning-fork example, several baselines generate broad or unstable energy patterns, while PAVAS better preserves the sustained resonance structure visible in the ground-truth spectrogram. The figure does not prove perfect physical correctness, but it supports the paper's main claim: explicit physics cues make the generated audio respond more consistently to visible impacts and resonant events.

### 5. Impact

PAVAS shifts video-to-audio synthesis from "match the visual category" toward "match the physical event." That matters for film Foley, generated video post-production, robotics simulation, AR, and any application where audio needs to react to object motion rather than merely label it. The benchmark contribution is also important: VGG-Impact and APCC give researchers a way to ask whether a generated sound changes with kinetic energy, not just whether it sounds realistic in isolation. The broader lesson is that multimodal generative models may need compact physical variables when the target signal is governed by real-world dynamics.

### 6. Further Reading

[1] [MMAudio: Taming Multimodal Joint Training for High-Quality Video-to-Audio Synthesis (2025)](https://arxiv.org/abs/2412.15322)<br>
The strongest direct backbone reference for PAVAS, using multimodal joint training and flow matching for high-quality synchronized video-to-audio generation.<br>
[2] [FoleyCrafter: Bring Silent Videos to Life with Lifelike and Synchronized Sounds (2024)](https://arxiv.org/abs/2407.01494)<br>
A text-guided video-to-audio framework that separates semantic alignment from temporal control through adapter modules.<br>
[3] [Temporally Aligned Audio for Video with Autoregression (2025)](https://arxiv.org/abs/2409.13689)<br>
Introduces V-AURA, an autoregressive V2A model focused on fine-grained temporal alignment and video-audio relevance.<br>
[4] [TARO: Timestep-Adaptive Representation Alignment with Onset-Aware Conditioning for Synchronized Video-to-Audio Synthesis (2025)](https://arxiv.org/abs/2504.05684)<br>
Uses onset-aware conditioning and timestep-adaptive alignment to improve synchronization for visually driven sound events.<br>
[5] [VAFlow: Video-to-Audio Generation with Cross-Modality Flow Matching (2025)](https://openaccess.thecvf.com/content/ICCV2025/html/Wang_VAFlow_Video-to-Audio_Generation_with_Cross-Modality_Flow_Matching_ICCV_2025_paper.html)<br>
Reframes V2A as direct video-to-audio flow matching rather than a generic noise-to-audio denoising path.<br>
[6] [StereoFoley: Object-Aware Stereo Audio Generation from Video (2025)](https://arxiv.org/abs/2509.18272)<br>
Extends V2A toward object-aware stereo generation, making spatial object-audio correspondence a central evaluation target.<br>
