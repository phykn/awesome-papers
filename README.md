# 🤖 Agentic Research Paper Reviews

Powered by an autonomous AI agent, this project delivers structured research paper reviews by dissecting complex architectures and pipelines. Every entry is end-to-end synthesized—from figure extraction to multilingual insight generation—to make high-level engineering concepts intuitively accessible.

|  No.  | Title                                                   | Category             | Year  |                     Korean                      |                     English                     |                    Japanese                     |                     Chinese                     |
| :---: | :------------------------------------------------------ | :------------------- | :---: | :---------------------------------------------: | :---------------------------------------------: | :---------------------------------------------: | :---------------------------------------------: |
|   1   | **GAN**: Generative Adversarial Nets                    | Image / GAN          | 2014  |           [View](./asset/gan/kor.md)            |           [View](./asset/gan/eng.md)            |                        —                        |                        —                        |
|   2   | **WGAN**: Wasserstein Generative Adversarial Networks   | Image / GAN          | 2017  |     [View](./asset/wasserstein_gan/kor.md)      |     [View](./asset/wasserstein_gan/eng.md)      |                        —                        |                        —                        |
|   3   | **NeRF**: Representing Scenes as Neural Radiance Fields | Image / 3D           | 2020  |           [View](./asset/nerf/kor.md)           |           [View](./asset/nerf/eng.md)           |           [View](./asset/nerf/jpn.md)           |           [View](./asset/nerf/zho.md)           |
|   4   | **SliceGAN**: Generating 3D Structures from a 2D Slice  | Material / GAN       | 2021  |        [View](./asset/slice_gan/kor.md)         |        [View](./asset/slice_gan/eng.md)         |        [View](./asset/slice_gan/jpn.md)         |        [View](./asset/slice_gan/zho.md)         |
|   5   | **ViT**: Vision Transformer for Image Recognition       | Image / Transformer  | 2021  |    [View](./asset/vision_transformer/kor.md)    |    [View](./asset/vision_transformer/eng.md)    |    [View](./asset/vision_transformer/jpn.md)    |    [View](./asset/vision_transformer/zho.md)    |
|   6   | **Zip-NeRF**: Anti-Aliased Grid-Based NeRF              | Image / 3D           | 2023  |         [View](./asset/zip_nerf/kor.md)         |         [View](./asset/zip_nerf/eng.md)         |         [View](./asset/zip_nerf/jpn.md)         |         [View](./asset/zip_nerf/zho.md)         |
|   7   | **3D Gaussian Splatting** for Real-Time Rendering       | Image / 3D           | 2023  |    [View](./asset/gaussian_splatting/kor.md)    |    [View](./asset/gaussian_splatting/eng.md)    |    [View](./asset/gaussian_splatting/jpn.md)    |    [View](./asset/gaussian_splatting/zho.md)    |
|   8   | **MASt3R**: Grounding Image Matching in 3D              | Image / 3D           | 2024  |          [View](./asset/mast3r/kor.md)          |          [View](./asset/mast3r/eng.md)          |          [View](./asset/mast3r/jpn.md)          |          [View](./asset/mast3r/zho.md)          |
|   9   | **Micro3Diff**: Multi-plane denoising diffusion         | Material / Diffusion | 2024  |        [View](./asset/micro3diff/kor.md)        |        [View](./asset/micro3diff/eng.md)        |        [View](./asset/micro3diff/jpn.md)        |        [View](./asset/micro3diff/zho.md)        |
|  10   | **GLOMAP**: Global Structure-from-Motion Revisited      | Image / 3D           | 2024  |   [View](./asset/global_sfm_revisited/kor.md)   |   [View](./asset/global_sfm_revisited/eng.md)   |   [View](./asset/global_sfm_revisited/jpn.md)   |   [View](./asset/global_sfm_revisited/zho.md)   |
|  11   | **VGGT**: Visual Geometry Grounded Transformer          | Image / 3D           | 2025  |           [View](./asset/vggt/kor.md)           |           [View](./asset/vggt/eng.md)           |           [View](./asset/vggt/jpn.md)           |           [View](./asset/vggt/zho.md)           |
|  12   | **MicroLad**: 2D-to-3D Reconstruction and Generation    | Material / Diffusion | 2026  |         [View](./asset/microlad/kor.md)         |         [View](./asset/microlad/eng.md)         |         [View](./asset/microlad/jpn.md)         |         [View](./asset/microlad/zho.md)         |
|  13   | **FVO**: Fast Visual Odometry with Transformers         | Image / SLAM         | 2026  | [View](./asset/fvo_fast_visual_odometry/kor.md) | [View](./asset/fvo_fast_visual_odometry/eng.md) | [View](./asset/fvo_fast_visual_odometry/jpn.md) | [View](./asset/fvo_fast_visual_odometry/zho.md) |

---
> **Disclaimer**: All reviews are AI-generated for educational purposes. Content may contain minor inaccuracies; use with discretion.
> *Last updated: 2026-05-06*


### ⚡ Agentic Workflow

To generate a new research paper review, simply provide the PDF URL along with the instructions in [`prompt.md`](./prompt.md):

```text
@prompt.md {PDF_URL}
```


The AI agent autonomously handles the entire end-to-end pipeline:

- **Planning**: Logic mapping & anchoring architecture to technical variables.
- **Figure Extraction**: Precision diagram cropping with caption removal.
- **Link Validation**: Real-time web verification for years & official repos.
- **Multilingual Synthesis**: Multi-language generation with math stability.
- **Auto-Deployment**: Automated README updates & index synchronization.

*Generated assets are stored in the `asset/` directory for permanent access.*
