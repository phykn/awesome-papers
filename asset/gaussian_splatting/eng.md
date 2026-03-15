# 3D Gaussian Splatting for Real-Time Radiance Field Rendering

- **Authors**: Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, George Drettakis
- **Venue/Date**: SIGGRAPH 2023 / August 2023
- **URL**: [https://arxiv.org/abs/2308.04079](https://arxiv.org/abs/2308.04079)
- **GitHub**: [https://github.com/graphdeco-inria/gaussian-splatting](https://github.com/graphdeco-inria/gaussian-splatting)

---

### 1. Background
Neural Radiance Fields (NeRFs) revolutionized 3D scene representation by using continuous volumetric functions (MLPs) to represent density and color. However, NeRFs suffer from a fundamental speed-quality trade-off: they require thousands of expensive neural network queries per pixel, making real-time rendering extremely difficult. While recent methods like Instant-NGP or Plenoxels improved speed using grid-based structures, they often struggle with the fine details and high-frequency backgrounds of complex, large-scale scenes. A new approach was necessary to bridge the gap between "high audit quality" and "real-time interactive performance."

### 2. Intuition
Imagine you are a painter trying to represent a 3D scene. Instead of filling every point in a 3D grid with color (voxels) or trying to describe the whole scene with a single complex math formula (NeRF), you use a collection of fuzzy, semi-transparent **spray paint spots** (3D Gaussians). Some spots are round, while others are stretched thin like needles (anisotropic) to follow the edges of a table or the surface of a leaf. By layering these millions of colored "splats" on top of each other, you can recreate a complex image from any angle very quickly, just like how classic computer graphics renders triangles, but with the softness and detail of a photograph.

### 3. Breakthrough
The "Aha!" insight is substituting the expensive volumetric ray-marching of NeRF with **differentiable 3D Gaussian splats** rendered via a high-performance **tile-based rasterizer**. By representing the scene as an explicit set of millions of ellipsoids that can be projected into 2D, the authors enabled the use of hardware-accelerated sorting and blending. This shift from implicit (querying a function) to explicit (drawing a primitive) allowed them to achieve the visual quality of the best NeRF models while rendering at over 100 frames per second.

### 4. Technical Mechanism

#### 4.1 Pipeline
![Pipeline Figure](figures/fig02_pipeline.png)
- The workflow begins with a sparse point cloud from Structure-from-Motion (SfM), which is converted into a set of 3D Gaussians. These Gaussians are optimized for position, rotation, scale, opacity, and color (Spherical Harmonics) through a fast, tile-based differentiable rasterizer that enables real-time feedback.
- (1) The figure shows the end-to-end transition from sparse input points to a dense, optimized radiance field. (2) Notice the "Adaptive Density Control" step which is crucial for filling gaps in the scene.

#### 4.2 Architecture / Core Design
![Architecture Figure](figures/fig04_densification.png)
- The core logic of the system is the **Adaptive Gaussian Densification**. Instead of using a fixed number of Gaussians, the model dynamically creates more "splats" where the scene is complex or under-reconstructed. It "clones" small Gaussians to cover empty spaces and "splits" large, blurry Gaussians into smaller, sharper ones to capture fine details.
- (1) This figure illustrates how the model identifies regions of "Under-Reconstruction" vs "Over-Reconstruction." (2) The "Split" and "Clone" operations allow the model to automatically adjust its resolution to match the scene complexity.

#### 4.3 Core Equation
- **Selection criteria**: This equation describes how the 3D covariance matrix (the shape of the Gaussian) is parameterized so it can be safely optimized using gradient descent while remaining physically valid (positive semi-definite).
- **Equation**: $\Sigma = R S S^T R^T$
- This formula decomposes the shape of a Gaussian ellipsoid into two independent components: the stretching (Scaling $S$) and the orientation (Rotation $R$).
- **Variables**:
  - $\Sigma$ = 3D Covariance matrix representing the Gaussian's shape and size.
  - $R$ = Rotation matrix derived from an optimized unit quaternion $q$.
  - $S$ = Scaling matrix derived from an optimized 3D vector $s$.

#### 4.4 Comparison: Others vs This Paper
3D Gaussian Splatting represents a paradigm shift from implicit neural volumes to explicit point-based splatting. The strongest baseline, Mip-NeRF360, provides excellent image quality but requires several minutes to render a single frame. In contrast, this paper achieves equal or better quality (Sec 7.1) while rendering in real-time. By moving away from MVS-based geometry and opting for anisotropic Gaussians, the method avoids the artifacts common in point-based rendering (Fig 11) and the training overhead of dense grids. The main trade-off is the memory requirement for storing millions of Gaussians, which can reach several gigabytes for complex scenes (Sec 7.5).

#### 4.5 Qualitative Results
![Qualitative Results](figures/fig05_qualitative.png)
The results demonstrate superior reconstruction of fine, thin structures like the spokes of a bicycle or the leaves in a garden, where previous methods like Instant-NGP often produce blurry or "pixelated" artifacts. When compared side-by-side with Mip-NeRF360, the images are visually indistinguishable in terms of sharpness and view-dependent reflections. As shown in the "Bicycle" and "Garden" scenes, our method preserves the specular highlights on metallic surfaces and the intricate textures of natural objects better than Plenoxels (Table 1 / Fig 5). One limitation is the occasional presence of "needle-like" artifacts in extremely sparse regions when view-dependent effects are not fully converged.

### 5. Impact
This paper effectively ended the "slow rendering" era of high-quality radiance fields. By providing a real-time, differentiable rasterization pipeline, it paved the way for applications in Virtual Reality, digital twins, and real-time cinematic rendering. 3D Gaussian Splatting has since become the new de facto standard for explicit radiance field research, spawning dozens of follow-up works focusing on compression, animation, and large-scale mapping.

### 6. Further Reading
- [SuGaR: Surface-Aligned Gaussian Splatting](https://arxiv.org/abs/2311.16523) - A method to extract high-quality meshes from Gaussians by aligning them to the scene surface.
- [4D Gaussian Splatting for Real-Time Dynamic Scene Rendering](https://arxiv.org/abs/2310.08585) - Extends the representation to dynamic scenes with moving objects.
- [GaussianPro: 3D Gaussian Splatting with Progressive Propagation](https://arxiv.org/abs/2402.14650) - Improves the density control mechanism for even better quality on complex geometry.
- [Compact 3D Gaussian Splatting](https://arxiv.org/abs/2311.13681) - Addresses the memory bottleneck by compressing the Gaussian representation.
- [Zip-NeRF: Anti-Aliased Grid-Based Neural Radiance Fields](https://arxiv.org/abs/2304.06706) - While published around the same time, it represents the pinnacle of the grid-based NeRF approach for comparison.
