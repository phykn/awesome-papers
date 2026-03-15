# NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis

- **Authors**: Ben Mildenhall, Pratul P. Srinivasan, Matthew Tancik, Jonathan T. Barron, Ravi Ramamoorthi, Ren Ng
- **Venue/Date**: ECCV 2020
- **URL**: [https://arxiv.org/abs/2003.08934](https://arxiv.org/abs/2003.08934)
- **GitHub**: [https://github.com/bmild/nerf](https://github.com/bmild/nerf)

---

### 1. Background
Previous approaches to view synthesis often relied on discrete representations such as voxel grids, meshes, or multi-plane images. These methods were constrained by their memory consumption—voxels scale cubically with resolution—leading to blurry results or limited scene complexity. Sparse representations like meshes struggled with complex topology or transparency. A new approach was necessary to represent detailed scenes continuously without the fixed memory overhead of a grid, enabling the synthesis of high-resolution images with complex geometry and appearance.

### 2. Intuition
Imagine a 3D volume filled with a semi-transparent fog, where every point in space has a specific density and a color that changes depending on the angle you look at it. This "fog" isn't a solid object but a continuous property of space. The core logic of NeRF matches this by treating a scene not as a collection of surfaces, but as a continuous field of "radiance" and "opacity." When you look at a pixel, you are effectively shining a flashlight (a ray) through this fog and accumulating the light it reflects back to you, which mirrors the physical process of light transport.

### 3. Breakthrough
The "Aha!" insight of this paper is to replace discrete scene storage (like voxels) with a continuous function parameterized by a neural network. Instead of looking up a value in a table, we query a Multi-Layer Perceptron (MLP) with a 3D coordinate and a 2D viewing direction to get the density and color. This "coordinate-based" representation allows the scene's resolution to be limited only by the capacity of the network, not by a physical grid size.

### 4. Technical Mechanism

#### 4.1 Pipeline
![Pipeline Figure](figures/fig02_pipeline.png)
- (1) This figure shows the end-to-end process from 2D pixel rays to 3D sampling and volume rendering. (2) Sampling points along the camera ray (a) is the first step before querying the neural radiance field.

#### 4.2 Architecture
![Architecture Figure](figures/fig07_architecture.png)
- (1) This figure depicts the MLP structure where 3D location and 2D viewing direction are processed separately. (2) The density $\sigma$ is predicted using only the location to ensure geometric consistency across views, while color $\mathbf{c}$ is view-dependent.

#### 4.3 Core Equation
- **Equation**: $C(\mathbf{r}) = \int_{t\_n}^{t\_f} T(t) \sigma(\mathbf{r}(t)) \mathbf{c}(\mathbf{r}(t), \mathbf{d}) dt$, where $T(t) = \exp\left(-\int_{t\_n}^t \sigma(\mathbf{r}(s)) ds\right)$
- The formula calculates the expected color of a camera ray by integrating the density and color of all points along the ray from the near to the far plane. $T(t)$ acts as a "transmittance" factor, representing the probability that light can travel from the point to the camera without hitting any other particles.
- **Variables**:
  - $C(\mathbf{r})$: The final RGB color predicted for ray $\mathbf{r}$ (Eq 2 / Sec 4).
  - $\sigma(\mathbf{x})$: The volume density at point $\mathbf{x}$, representing the differential probability of a ray hitting a particle (Eq 1 / Sec 3).
  - $\mathbf{c}(\mathbf{x}, \mathbf{d})$: The view-dependent RGB color at point $\mathbf{x}$ as seen from direction $\mathbf{d}$ (Eq 1 / Sec 3).
  - $T(t)$: Accumulated transmittance along the ray from $t\_n$ to $t$ (Eq 3 / Sec 4).

#### 4.4 Comparison: Others vs This Paper
NeRF significantly outperforms prior methods like SRN and NV in capturing fine, high-frequency textures and complex specular reflections. While SRN fails to maintain sharpness and NV is limited by voxel resolution, NeRF utilizes positional encoding and hierarchical sampling to achieve state-of-the-art results (Sec 6 / Table 1). The use of continuous MLP-based representations eliminates discretization artifacts common in multi-plane images. However, NeRF requires extensive optimization time for each new scene, often taking 1–2 days on a single GPU (Sec 6). The method’s core differentiator is the combination of coordinate-based neural representations with classical volume rendering.

#### 4.5 Qualitative Results
![Qualitative Results](figures/fig06_qualitative.png)
The qualitative comparison highlights NeRF's ability to reconstruct intricate details and realistic non-Lambertian effects that baselines like SRN, NV, and LLFF fail to capture. On synthetic objects from the "Realistic Synthetic 360°" dataset, NeRF produces significantly sharper results and fewer visual artifacts compared to SRN and LLFF. SRN often outputs overly smooth or blurry surfaces, while NV suffers from visible voxelization. LLFF exhibits ghosting and lack of multiview consistency in complex regions. NeRF's results are visually indistinguishable from the ground truth in many cases (Fig 6).

### 5. Impact
NeRF revolutionized computer vision and graphics by proving that complex 3D scenes can be efficiently stored and rendered using neural networks as continuous functions. It sparked a massive wave of research into Neural Radiance Fields, leading to advancements in 3D reconstruction, robotics, and virtual reality. The method's success directly inspired high-speed variants like Instant-NGP and large-scale applications like Block-NeRF.

### 6. Further Reading
[1] [Mip-NeRF: A Multiscale Representation for Anti-Aliasing Neural Radiance Fields (2021)](https://arxiv.org/abs/2103.13415)<br>
Fixes aliasing issues and improves rendering quality at different scales.<br>
[2] [Instant Neural Graphics Primitives with a Multiresolution Hash Encoding](https://nvlabs.github.io/instant-ngp/)<br>
Dramatically speeds up training and rendering from days to seconds.<br>
[3] [NeRF in the Wild: Neural Radiance Fields for Unconstrained Photo Collections](https://nerf-w.github.io/)<br>
Adapts NeRF to handle varying lighting and transient objects in tourist photos.<br>
[4] [Block-NeRF: Scalable Neural Radiance Fields for Entire City Blocks](https://waymo.com/research/block-nerf/)<br>
Scales NeRF to represent large-scale environments like entire city streets.<br>
[5] [RawNeRF: Preparing for Real HDR View Synthesis with Neural Radiance Fields](https://bmild.github.io/rawnerf/)<br>
Trains directly on raw camera data to enable high dynamic range view synthesis and denoising.<br>
