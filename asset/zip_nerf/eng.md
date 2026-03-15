# Zip-NeRF: Anti-Aliased Grid-Based Neural Radiance Fields
- **Authors**: Jonathan T. Barron, Ben Mildenhall, Dor Verbin, Pratul P. Srinivasan, Peter Hedman
- **Venue/Date**: ICCV 2023
- **URL**: https://arxiv.org/abs/2304.06706
- **GitHub**: https://github.com/google-research/zip-nerf

### 1. Background
Standard Neural Radiance Fields (NeRF) suffer from two major problems: slow training/rendering and aliasing (jaggies). Mip-NeRF addressed aliasing using conical frustums, but was slow. Instant NGP introduced fast grid-based representations, but brought back aliasing because it samples discrete points. Zip-NeRF aims to merge the best of both worlds: the speed of grids and the anti-aliasing of conical frustums.

### 2. Intuition
Imagine trying to color a grid with a very fine brush (grid-based NeRF). If you move the brush slightly, the colors change abruptly (aliasing). Zip-NeRF is like using multiple tiny brushes for each pixel and averaging their colors before applying them to the grid, ensuring a smooth transition no matter how you move.

### 3. Breakthrough
The core breakthrough is a multisampling strategy that integrates Instant NGP's grid pyramid into mip-NeRF 360’s framework. By using a hexagonal multisampling pattern and a prefiltered loss, the model can 'reason' about the scale of the grid voxels without sacrificing the speed of hash-based encoding.

### 4. Technical Mechanism

#### 4.1 Pipeline
![Pipeline Figure](figures/fig02_pipeline.png)
- The pipeline integrates a multiresolution hash-grid with a multisampling strategy. Instead of a single point, 6 points are sampled per interval in a hexagonal pattern to represent the conical frustum volume.
- Key module: Multiresolution hash-grid combined with 6-point hexagonal multisampling per frustum.

#### 4.2 Architecture / Core Design
![Architecture Figure](figures/fig03_architecture.png)
- The architecture uses a multisampled featurization where grid features are averaged across samples. This allows the MLP to receive a 'scale-aware' input that matches the resolution of the grid at that depth.
- Design rationale: Scale-aware input featurization prevents high-frequency noise from leaking into the MLP (Fig 3).

#### 4.3 Core Equation
- The scale-aware feature $f$ is computed by averaging trilinearly interpolated hash-grid features over multiple samples:
- $$f(\mathbf{x}, \sigma) = \frac{1}{J} \sum_{j=1}^{J} \text{tri}(\text{hash}(\mathbf{x}_j))$$
- Variables:
- $\mathbf{x}_j$: $j$-th multisample coordinate within the conical frustum (Fig 3).
- $\sigma$: Scale parameter determining the spread of samples.
- $\text{tri}$: Trilinear interpolation on the hash-grid features (Eq 2).
- $J$: Number of samples (fixed at 6 in this paper).

#### 4.4 Comparison: Others vs This Paper
Zip-NeRF significantly outperforms both mip-NeRF 360 and Instant NGP. While mip-NeRF 360 provides high-quality anti-aliasing, it is prohibitively slow for large-scale training. Instant NGP is fast but produces severe aliasing artifacts (jaggies) when zoomed in or out (Sec 4.1). Zip-NeRF achieves lower error rates (8% to 77% reduction) while training 24x faster than mip-NeRF 360 (Fig 1). The main trade-off is a slightly higher memory footprint due to the multisampled features, but the speed-quality gains are substantial.

#### 4.5 Qualitative Results
![Qualitative Results](figures/fig01_teaser.png)
- Qualitative results demonstrate that Zip-NeRF excels at recovering fine, thin structures like leaves and railings that are typically lost or aliased in grid-based models. Comparison with ground truth (Fig 1) shows that Zip-NeRF's renderings are virtually indistinguishable from real images, whereas previous fast methods show noticeable flickering and noise.

### 5. Impact
Zip-NeRF sets a new standard for efficient and high-quality view synthesis. It bridges the gap between 'research-grade' quality and 'production-grade' speed, making radiance fields more practical for real-world applications like VR and high-end digital twins.

### 6. Further Reading

[1] [Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields (2021)](https://arxiv.org/abs/2111.12077)<br>
The predecessor that introduced non-linear scene contracting and anti-aliased conical frustums for unbounded scenes.<br>
[2] [Instant Neural Graphics Primitives with a Multiresolution Hash Encoding (2022)](https://arxiv.org/abs/2201.05989)<br>
Introduced the fast hash-grid-based featurization that Zip-NeRF optimizes for anti-aliasing.<br>
[3] [3D Gaussian Splatting for Real-Time Radiance Field Rendering (2023)](https://arxiv.org/abs/2308.04079)<br>
A competing state-of-the-art method using explicit point-based primitives instead of volumetric fields.<br>
[4] [MERF: Memory-Efficient Radiance Fields for Real-Time View Synthesis (2023)](https://arxiv.org/abs/2302.12249)<br>
A hybrid representation focused on real-time browser-based rendering of radiance fields.<br>
[5] [NeRF: Representing Scenes as Neural Radiance Fields (2020)](https://arxiv.org/abs/2003.08934)<br>
The foundational work that started the neural radiance field revolution.<br>

