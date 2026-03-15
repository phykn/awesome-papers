# MicroLad: Latent Diffusion-Based 2D-to-3D Microstructure Reconstruction with Inverse Design

- **Authors**: Kang-Hyun Lee, Gun Jin Yun
- **Venue/Date**: Preprint (2025)
- **URL**: [https://arxiv.org/abs/2505.00000](https://github.com/KangHyunL/microlad)
- **GitHub**: [https://github.com/KangHyunL/microlad](https://github.com/KangHyunL/microlad)

---

### 1. Background
Acquiring representative 3D microstructure datasets is critical for integrated computational materials engineering (ICME), yet obtaining them remains prohibitively expensive due to high experimental costs (e.g., X-ray CT, serial sectioning). While 2D micrographs are relatively easy to obtain, existing 2D-to-3D reconstruction methods—whether descriptor-based (e.g., two-point correlation matching) or data-driven (e.g., GANs, diffusion models)—face fundamental limitations. Descriptor-based methods are constrained by the information content of chosen descriptors: distinct microstructures can share nearly identical statistics. Data-driven methods like SliceGAN or multi-plane denoising diffusion (MPDD) can reconstruct statistically equivalent 3D volumes, but they cannot generate microstructures *beyond* the training distribution, limiting design space exploration. A framework capable of both faithful reconstruction *and* inverse-controlled generation toward target properties was needed.

### 2. Intuition
Imagine you have a 2D photograph of a material's cross-section and want to build a full 3D model that not only looks right from every angle but also achieves a specific target property (e.g., maximum diffusivity). MicroLad works like a sculptor who first learns to carve realistic slices from any direction (using a pre-trained 2D latent diffusion model), then assembles them into a 3D block while checking consistency from three orthogonal views. The key twist is an additional "coaching signal" (Score Distillation Sampling) that nudges each slice toward the desired physical properties—like a coach guiding a painter to not just draw realistic textures but to arrange them so the final structure conducts heat optimally.

### 3. Breakthrough
The decisive insight of MicroLad is combining **latent diffusion-based 2D-to-3D reconstruction** with **Score Distillation Sampling (SDS)** for inverse design. Previous diffusion-based methods could reconstruct 3D microstructures but were limited to reproducing the training distribution. MicroLad breaks this barrier by operating in a learned latent space (via a pretrained VAE), performing multi-plane denoising diffusion for 3D coherence, and then applying SDS to steer the generation toward user-specified targets—microstructural descriptors (volume fraction, surface area) or effective material properties (diffusivity)—all without retraining the diffusion model.

### 4. Technical Mechanism

#### 4.1 Pipeline
![Pipeline Figure](figures/fig01_pipeline.png)
- (1) This figure shows the end-to-end MicroLad framework: (a) acquiring 2D microstructure data, (b) encoding it into a latent space via a pretrained VAE, (c) training a latent diffusion model, (d) performing latent multi-plane denoising diffusion (L-MPDD) for 2D-to-3D reconstruction, and (e) applying SDS-based inverse control. (2) The critical design choice is performing all diffusion operations in the compressed latent space rather than pixel space, dramatically reducing computational cost.

#### 4.2 Architecture
![Comparison Figure](figures/fig02_comparison.png)
- (1) This figure contrasts the conventional computational materials engineering workflow (forward SP linkage only) with the MicroLad approach that enables both forward and inverse SP linkages. (2) The key architectural innovation is closing the loop: rather than only predicting properties from structure, MicroLad can generate structures that target specific properties via SDS-guided optimization in latent space.

#### 4.3 Core Equation
- **Equation**: $\mathcal{L}\_{\text{SDS}} = \kappa(t) \|\epsilon - \epsilon\_\theta(z\_{\text{slice},t}, t)\|^2$, where $\kappa(t) = \frac{1 - \bar{\alpha}\_t}{\bar{\alpha}\_t}$
- The SDS loss measures how well the current latent slice matches the distribution learned by the frozen diffusion model. Combined with descriptor matching loss $\mathcal{L}\_M = \|M(\hat{x}\_{\text{slice}}) - M^\*\|^2$ and property loss $\mathcal{L}\_P = \|H(\hat{x}\_{\text{slice}}) - P^\*\|^2$, the total gradient steers the latent representation toward realistic microstructures with desired target properties.
- **Variables**:
  - $\epsilon\_\theta$ = The frozen pretrained denoising network (U-Net) that provides the diffusion prior (Sec 3.4 / Eq 39).
  - $z\_{\text{slice}}$ = Latent representation of a 2D slice encoded by the VAE encoder $E$ (Sec 3.4 / Eq 37).
  - $M^\*$, $P^\*$ = User-specified target microstructural descriptors and effective material properties (Sec 3.4 / Eq 42–43).
  - $H$ = Differentiable physics solver (FEM) for computing effective diffusivity (Sec 3.4 / Eq 43).

#### 4.4 Comparison: Others vs This Paper
MicroLad significantly extends the capabilities of prior diffusion-based microstructure reconstruction methods. While MPDD (Micro3Diff) could reconstruct 3D volumes statistically equivalent to 2D training data, it could not generate microstructures with controlled target properties. SliceGAN, a GAN-based approach, suffers from mode collapse and lacks property-guided generation. MicroLad operates in latent space (4×16×16 vs full-resolution pixel space), reducing computational cost while maintaining fidelity. The two-point correlation function ($S\_2$) error rates for reconstructed binary and three-phase microstructures are consistently below 5% (Sec 4.1 / Fig 3–4). Crucially, MicroLad demonstrates successful inverse-controlled generation for volume fraction, surface area, and relative diffusivity targets (Sec 4.2 / Fig 5–7). The trade-off is the requirement for a differentiable physics solver for property-guided generation, which limits applicability to properties that can be efficiently differentiated (Sec 3.4).

#### 4.5 Qualitative Results
![Qualitative Results - Binary](figures/fig03_qualitative.png)
The qualitative results for binary carbonate microstructures demonstrate that MicroLad faithfully reconstructs 3D volumes whose cross-sections are visually indistinguishable from the original 2D training images. The two-point correlation functions ($S\_2$) and lineal path functions ($L\_2$) show excellent agreement between generated and original samples across all three orthogonal directions (Fig 3d). The reconstructed 3D volumes exhibit realistic pore connectivity and spatial heterogeneity characteristic of real carbonate microstructures.

![Qualitative Results - Three Phase](figures/fig04_qualitative_threephase.png)
For three-phase SOFC (solid oxide fuel cell) microstructures, MicroLad successfully captures the distinct morphology of each phase—pore, ionic conductor, and electronic conductor—while maintaining their spatial interrelationships. The $S\_2$ and $L\_2$ functions for all three phases closely match those of the original samples, confirming morphological fidelity (Fig 4d). This is particularly noteworthy given the added complexity of multi-phase structures where inter-phase boundaries must remain physically consistent.

### 5. Impact
MicroLad represents a significant step toward closing the loop between microstructure characterization and materials design. By combining latent diffusion models with score distillation sampling and differentiable physics solvers, it enables researchers to not only reconstruct realistic 3D microstructures from 2D observations but also to inversely design microstructures targeting specific material properties. This capability is directly relevant to accelerating ICME workflows for energy materials (SOFCs, batteries), structural composites, and other systems where 3D microstructure governs performance.

### 6. Further Reading
- [Multi-plane denoising diffusion-based dimensionality expansion (Micro3Diff)](https://doi.org/10.1038/s41524-024-01280-z) - The predecessor framework by the same authors, establishing multi-plane denoising diffusion for 2D-to-3D reconstruction.
- [Score Distillation Sampling (DreamFusion)](https://arxiv.org/abs/2209.14988) - The foundational technique for distilling knowledge from 2D diffusion models into 3D representations.
- [SliceGAN: Generating 3D Structures from a 2D Slice with GAN-based Dimensionality Expansion](https://arxiv.org/abs/2102.07708) - A GAN-based baseline for 2D-to-3D microstructure generation.
- [Latent Diffusion Models (Stable Diffusion)](https://arxiv.org/abs/2112.10752) - The core latent diffusion architecture that MicroLad builds upon.
