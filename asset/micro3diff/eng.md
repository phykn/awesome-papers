# Multi-plane denoising diffusion-based dimensionality expansion for 2D-to-3D reconstruction of microstructures with harmonized sampling

- **Authors**: Kang-Hyun Lee, Gun Jin Yun
- **Venue/Date**: npj Computational Materials (2024)
- **URL**: [https://doi.org/10.1038/s41524-024-01280-z](https://doi.org/10.1038/s41524-024-01280-z)
- **GitHub**: Not specified in the paper.

---

### 1. Background
Characterizing 3D microstructures is essential for understanding material properties, but acquiring 3D datasets (e.g., via X-ray CT or serial sectioning) is extremely costly and time-consuming. In contrast, 2D micrographs are abundant and easy to obtain. Previous 2D-to-3D reconstruction methods often relied on heavy 3D training data or struggled with maintaining spatial connectivity and physical realism in the third dimension. There was a critical need for a framework that could expand 2D knowledge into 3D without expensive 3D training.

### 2. Intuition
The core intuition is that a valid 3D structure should look like a realistic 2D image when sliced from any orthogonal direction (XY, YZ, and ZX planes). Imagine a sculptor carving a 3D object: by constantly checking and refining the shape from the front, side, and top, they ensure the final piece is consistent. Micro3Diff applies this by using a pre-trained 2D diffusion model to simultaneously "denoise" or "refine" slices from all three directions, forcing them to harmonize into a single, connected 3D volume.

### 3. Breakthrough
The "Aha!" insight of Micro3Diff is performing **dimensionality expansion during the inference (sampling) stage** rather than the training stage. This means we can leverage existing, high-quality 2D Diffusion Generative Models (DGMs) and only enforce 3D consistency during the denoising process. This eliminates the need for any 3D training data, making the framework exceptionally flexible and efficient for materials scientists.

### 4. Technical Mechanism

#### 4.1 Pipeline
![Pipeline Figure](figures/fig13_pipeline.png)
- (1) This figure illustrates the "multi-plane denoising" process donde noisy 3D voxels are sliced into three orthogonal planes (XY, YZ, ZX). (2) Each slice is processed by the 2D DGM, and the resulting updates are aggregated back into the 3D volume to maintain spatial connectivity.

#### 4.2 Architecture
![Algorithm Figure](figures/fig16_algorithm.png)
- (1) This diagram shows the "Harmonized Sampling" algorithm which manages the noise levels across dimensions. (2) It addresses the potential mapping errors when moving from 2D latent spaces to 3D structures, ensuring the reverse diffusion stays on a stable trajectory.

#### 4.3 Core Equation
- **Equation**: $\hat{x}_{t-1, i} = \text{MultiPlaneDenoise}(x_{t, i}, \epsilon_\theta, \text{ planes} \in \{XY, YZ, ZX\})$
- The process iteratively refines the 3D volume $x$ by ensuring that the denoised estimate from each plane contributes to the final voxel value. This is typically implemented as a weighted average or a specific sampling step in the diffusion reverse process.
- **Variables**:
  - $x_t$ = The 3D noisy volume at time step $t$ (Sec 4.1).
  - $\epsilon_\theta$ = The pre-trained 2D denoising neural network (U-Net) (Sec 4.2).
  - $t$ = Diffusion time step, ranging from noise to pure data (Sec 4.1).

#### 4.4 Comparison: Others vs This Paper (Evidence-Based)
Micro3Diff demonstrates superior 3D connectivity and morphological accuracy compared to standard slice-by-slice generation. While conventional 2D methods lack out-of-plane consistency, Micro3Diff ensures that two-point correlation functions ($S_2$) and lineal path functions ($L_2$) are statistically equivalent across all directions (Sec 3 / Fig 4). The harmonized sampling process significantly reduces the error rates in capturing complex features like polycrystalline grain boundaries compared to naive multi-plane approaches (Fig 5). A notable trade-off is the increased computational time per 3D volume due to the triple-plane denoising loop (Sec 3.1).

#### 4.5 Qualitative Results
![Qualitative Results](figures/fig02_qualitative.png)
The qualitative results show the successful reconstruction of diverse microstructures, including spherical inclusions, polycrystalline grains (case II), and complex porous structures like NMC cathodes. In "case II" (polycrystalline), the generated 3D samples display realistic grain connectivity and triple-junction geometry that matches the visual character of the original 2D training set (Fig 7). For porous media like the carbonate dataset, Micro3Diff captures the intricate network morphology and tortuosity that are critical for battery performance analysis (Fig 11).

### 5. Impact
Micro3Diff provides a powerful tool for Materials Informatics, allowing researchers to generate high-fidelity 3D microstructures from readily available 2D data. This significantly lowers the barrier to performing high-throughput simulations and integrated computational materials engineering (ICME). It effectively bridges the gap between easy 2D acquisition and necessary 3D characterization.

### 6. Further Reading (After This Paper)
- [MicroLad: Latent Diffusion-Based 2D-to-3D Microstructure Reconstruction with Inverse Design](https://github.com/KangHyunL/microlad) - Follow-up work that introduces latent space diffusion and score distillation for property-guided inverse design.
