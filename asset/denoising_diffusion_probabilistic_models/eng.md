# Denoising Diffusion Probabilistic Models

- **Authors**: Jonathan Ho, Ajay Jain, Pieter Abbeel
- **Venue/Date**: NeurIPS 2020
- **URL**: [https://arxiv.org/abs/2006.11239](https://arxiv.org/abs/2006.11239)
- **GitHub**: [https://github.com/hojonathanho/diffusion](https://github.com/hojonathanho/diffusion)

---

### 1. Background
Before DDPM, high-quality image generation was dominated by GANs and autoregressive models. GANs produced sharp images but were hard to train and did not give a direct likelihood; autoregressive models gave likelihoods but generated pixels sequentially and slowly. Earlier diffusion probabilistic models had a clean thermodynamic idea, but they had not yet shown GAN-level image quality. This paper was necessary because it showed that a very simple Gaussian noising-and-denoising chain could become a practical high-fidelity image generator.

### 2. Intuition
Imagine taking a clear photo and adding a tiny amount of static to it again and again until it becomes pure noise. That direction is easy because we choose the noise ourselves. The hard part is learning the reverse: from static, remove just the right amount of noise at each step until an image appears. DDPM turns generation into this repeated cleanup task. Instead of asking a network to create a whole image in one jump, it asks the network one smaller question many times: "what noise was added here?"

### 3. Breakthrough
The key insight is that the reverse diffusion step can be trained by predicting the injected Gaussian noise $\epsilon$, not by directly predicting the clean image or the full reverse mean. This turns a variational inference objective into a simple denoising loss that looks like denoising score matching across many noise levels. The result is engineering-friendly: sample a timestep, corrupt the image to that timestep, train a U-Net to predict the noise, then run the learned reverse chain from Gaussian noise back to data.

### 4. Technical Mechanism

#### 4.1 Pipeline
![Pipeline Figure](figures/fig02_pipeline.png)
- (1) The figure shows the two opposite Markov chains: the fixed forward process $q(x\_t \mid x\_{t-1})$ gradually destroys data into noise, while the learned reverse process $p\_\theta(x\_{t-1} \mid x\_t)$ generates data by denoising. (2) The central design variable is timestep $t$, because the same model must know how much noise to remove at each stage.

#### 4.2 Architecture / Core Design
- Pseudo-figure flow: clean image $x\_0$ -> choose timestep $t$ -> sample noise $\epsilon$ -> form noisy image $x\_t$ -> U-Net $\epsilon\_\theta(x\_t,t)$ -> predict the noise -> reverse update to $x\_{t-1}$.
- The core design choice is to share one U-Net across all timesteps and inject $t$ through sinusoidal position embeddings; this makes the network a conditional denoiser rather than a separate model for every noise level.

#### 4.3 Core Equation
- The simplified training objective captures the paper's practical novelty:

$$
L_{\mathrm{simple}}(\theta) = \mathbb{E}_{t,x_0,\epsilon}\left[\left\Vert \epsilon - \epsilon_\theta\left(\sqrt{\bar{\alpha}_t}x_0 + \sqrt{1-\bar{\alpha}_t}\epsilon, t\right) \right\Vert^2\right]
$$

- Variables:
  - $x\_0$: the original data sample, first introduced as the data endpoint of the latent chain (Sec 2 / Eq 1).
  - $x\_t$: the noisy version of $x\_0$ at timestep $t$, sampled in closed form from the forward process (Sec 2 / Eq 4).
  - $\epsilon$: standard Gaussian noise used to construct $x\_t$ (Sec 3.2 / Eq 9).
  - $\epsilon\_\theta(x\_t,t)$: the neural network's predicted noise at timestep $t$ (Sec 3.2 / Eq 11).
  - $\bar{\alpha}\_t$: cumulative product of noise-retention factors, controlling the signal-to-noise ratio at timestep $t$ (Sec 2 / Eq 4).

#### 4.4 Comparison: Others vs This Paper
The paper's claim is that diffusion models can produce high-quality images without adversarial training. Earlier diffusion models had the same broad forward/reverse idea, but their sample quality did not compete with leading generators. DDPM's differentiator is the $\epsilon$-prediction parameterization plus the unweighted $L\_{\mathrm{simple}}$ objective, which emphasizes harder denoising steps and is easy to implement (Sec 3.4). Empirically, the unconditional CIFAR-10 model reaches FID 3.17 and Inception Score 9.46, while the ablation table shows much worse FID when predicting the reverse mean directly (Table 1 / Table 2). The trade-off is sampling cost: generation requires many sequential denoising steps, so quality comes with slow inference.

#### 4.5 Qualitative Results
![Qualitative Results](figures/fig01_qualitative.png)
The sample figure shows that the model is not merely memorizing simple textures. On CelebA-HQ, faces have coherent global structure: eyes, hair, lighting, and facial symmetry stay aligned across the generated image. On CIFAR-10, the small samples cover many classes and viewpoints, showing that the model can represent a broad image distribution rather than one narrow mode.

The figure also makes the core trade-off visible. The images are strong enough to compete with GAN-era results, but they are generated through a long reverse chain rather than a single generator pass. DDPM therefore shifts the engineering problem from adversarial stability to denoising accuracy and sampling speed.

### 5. Impact
DDPM made diffusion models a central family of generative models. It gave researchers a stable recipe: add known Gaussian noise, train a conditional denoiser, and sample by reversing the chain. Later work accelerated sampling, generalized the continuous-time score/SDE view, added guidance, and moved diffusion into latent spaces for high-resolution text-to-image systems. The paper's lasting impact is that it turned diffusion from an elegant probabilistic idea into the default engineering backbone for modern image generation.

### 6. Further Reading
[1] [Deep Unsupervised Learning using Nonequilibrium Thermodynamics (2015)](https://arxiv.org/abs/1503.03585)<br>
Introduces the original diffusion probabilistic modeling idea that DDPM later makes visually competitive.<br>
[2] [Generative Modeling by Estimating Gradients of the Data Distribution (2019)](https://arxiv.org/abs/1907.05600)<br>
Develops score-based generation with annealed Langevin dynamics, a key conceptual neighbor of DDPM.<br>
[3] [Denoising Diffusion Implicit Models (2020)](https://arxiv.org/abs/2010.02502)<br>
Shows how to sample much faster by using non-Markovian reverse processes with the same DDPM training objective.<br>
[4] [Score-Based Generative Modeling through Stochastic Differential Equations (2021)](https://arxiv.org/abs/2011.13456)<br>
Unifies diffusion and score-based models through continuous-time SDEs and reverse-time sampling.<br>
[5] [Improved Denoising Diffusion Probabilistic Models (2021)](https://arxiv.org/abs/2102.09672)<br>
Improves likelihood and sampling efficiency by learning reverse-process variances and refining the objective.<br>
[6] [High-Resolution Image Synthesis with Latent Diffusion Models (2022)](https://arxiv.org/abs/2112.10752)<br>
Moves diffusion into an autoencoder latent space, making high-resolution conditional generation far cheaper.<br>
