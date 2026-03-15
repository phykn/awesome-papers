# Generating 3D Structures from a 2D Slice with GAN-Based Dimensionality Expansion

- **Authors**: Steve Kench, Samuel J. Cooper
- **Venue/Date**: Preprint - February 16, 2021 (arXiv:2102.07708)
- **URL**: [https://arxiv.org/abs/2102.07708](https://arxiv.org/abs/2102.07708)
- **GitHub**: [https://github.com/stke9/SliceGAN](https://github.com/stke9/SliceGAN)

---

### 1. Background
The physical and chemical properties of materials are significantly influenced by their 3D microstructure. However, obtaining high-fidelity 3D volumetric datasets (e.g., via X-ray tomography) is often time-consuming, expensive, and limited in resolution. In contrast, 2D micrographs (like SEM images) are easier to acquire and offer higher resolution but lack the volumetric depth required for accurate physical simulations. Previous statistical reconstruction methods often failed to capture complex, non-random topological features, creating a need for a generative approach that can perform "dimensionality expansion" from 2D to 3D.

### 2. Intuition
Imagine you are trying to recreate a complex 3D marble cake. You have never seen the whole cake, only thin slices of real cakes. The "SliceGAN" intuition is that if you can generate a 3D cake such that every slice you take from it—whether horizontally, vertically, or depth-wise—is indistinguishable from the real 2D slices you have, then your 3D cake must statistically match the real structure. It’s like learning the volume by mastering its cross-sections.

### 3. Breakthrough
The core breakthrough of SliceGAN is the decoupling of the generator's dimensionality from the discriminator's dimensionality. While the generator produces a 3D volume, the discriminator only looks at 2D slices. This allows the model to be trained using only 2D image data to produce 3D volumes. By enforcing 1D-to-2D statistical consistency across multiple planes, the model effectively "hallucinates" the third dimension in a way that remains physically plausible for the material's microstructure.

### 4. Technical Mechanism

#### 4.1 Pipeline
![Pipeline Figure](figures/fig01_pipeline.png)
- The pipeline begins with a latent vector $z$ which the 3D generator transforms into a volumetric sample $f$. This volume is then sliced along the $x, y,$ and $z$ axes to produce 2D images, which a 2D discriminator compares against real training micrographs to provide feedback.
- Key modules: (1) 3D Generator $G$ for volume synthesis, (2) Slicing operation to bridge the 3D-2D gap.

#### 4.2 Architecture / Core Design
![Architecture Figure](figures/tab01_architecture.png)
- The architecture utilizes 3D transpose convolutions in the generator to expand a 1D latent vector into a $64^3$ volume, while the discriminator uses standard 2D convolutions to evaluate slices.
- Key design choice: Using a spatial input $z$ of $4 \times 4 \times 4$ instead of $1 \times 1 \times 1$ to avoid edge artifacts and ensure uniform information density across the generated volume.

#### 4.3 Core Equation
- **Selection criteria**: The optimization objective using the Wasserstein GAN loss with Gradient Penalty (WGAN-GP) to ensure stable training and high-quality synthesis.
- **Equation**:

$$ L\_D = \mathbb{E}[D(G(z)\_s)] - \mathbb{E}[D(r)] + \lambda \mathbb{E}[(\Vert \nabla\_{\hat{x}} D(\hat{x}) \Vert\_2 - 1)^2] $$

- This formula measures the "distance" between the distribution of fake slices and real images.
- **Variables**: 
    - $G(z)\_s$: 2D slice of the generated 3D volume (Page 3).
    - $r$: Real 2D training image (Page 3).
    - $\lambda$: Gradient penalty coefficient (used to stabilize training).

#### 4.4 Comparison: Others vs This Paper
SliceGAN significantly outperforms traditional stochastic and correlation-based reconstruction methods in capturing long-range connectivity and complex phases. Unlike standard 3D GANs that require volumetric training data, this approach works with widely available 2D micrographs. The paper demonstrates that once trained, SliceGAN can generate $10^8$ voxel volumes in seconds, representing a $10^5$ acceleration compared to conventional physical simulations. The method is shown to be robust across varied materials including polycrystalline grains, ceramic fibers, and battery electrodes (Sec 5.2 / Fig 3).

#### 4.5 Qualitative Results
![Qualitative Results](figures/fig03_qualitative.png)
The qualitative results showcase the successful reconstruction of diverse microstructures ranging from simple grains (Row A) to complex multi-phase battery separators (Row D). From left to right, the figure shows the original 2D training image, the generated 3D volume, and slices taken at different angles. Notably, the $45^\circ$ angle slices (rightmost columns) demonstrate that the generator has learned a consistent 3D representation rather than just memorizing axial orientations. While the grain boundaries in Row A show slight curvature not present in the original, the overall topological connectivity across all material types remains highly realistic (Fig 3).

### 5. Impact
SliceGAN provides a powerful tool for the materials science community, enabling the generation of representative 3D volumes for physics-based simulations (like stress analysis or fluid flow) from simple 2D imaging. This bridges the gap between high-resolution 2D data and the necessity for 3D volumetric analysis, potentially accelerating the discovery and optimization of next-generation energy materials and composites.

### 6. Further Reading
[1] [Super-resolution of multiphase materials by combining complementary 2D and 3D image data using generative adversarial networks (2021)](https://arxiv.org/abs/2110.11281)<br>
Combining 2D and 3D data for high-resolution reconstruction.<br>
[2] [Micro3Diff: Multi-plane denoising diffusion-based dimensionality expansion (2023)](https://arxiv.org/abs/2308.14035)<br>
Latest 2D-to-3D reconstruction using Diffusion Models.<br>
[3] [SliceGAN Github Issues/Discussions](https://github.com/stke9/SliceGAN)<br>
For practical implementation tips and follow-up community research.<br>
