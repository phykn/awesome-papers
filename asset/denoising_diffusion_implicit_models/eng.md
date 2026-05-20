# Denoising Diffusion Implicit Models

- **Authors**: Jiaming Song, Chenlin Meng, Stefano Ermon
- **Venue/Date**: ICLR 2021
- **URL**: [https://arxiv.org/abs/2010.02502](https://arxiv.org/abs/2010.02502)
- **GitHub**: [https://github.com/ermongroup/ddim](https://github.com/ermongroup/ddim)

---

### 1. Background
DDPM proved that diffusion models could generate high-quality images without adversarial training, but it exposed a serious engineering bottleneck: sampling required hundreds or thousands of sequential denoising steps. That made diffusion much slower than GANs, which use a single generator pass. The key question was whether the same trained denoising network could be used with a shorter generation path. DDIM was necessary because it showed that the slow Markov chain was not the only valid way to sample from a DDPM-trained model.

### 2. Intuition
Think of DDPM as walking down every stair in a tall building: each stair is safe, but the trip is slow. DDIM asks whether we can skip floors while still landing in the same lobby. The trick is not to retrain the person walking; it is to choose a different path through the same building. In diffusion terms, the model still learns to denoise noisy images, but sampling follows a shorter and often deterministic trajectory through selected timesteps.

### 3. Breakthrough
The breakthrough is to generalize DDPM's forward diffusion into a family of non-Markovian inference processes that preserve the same marginal distributions $q(x\_t \mid x\_0)$. Because the training objective depends on these marginals rather than on the exact full forward chain, the same DDPM-trained network can support many reverse processes. The deterministic case, where the added reverse noise term is removed, becomes DDIM: an implicit model that can sample much faster and gives a meaningful latent $x\_T$ for consistency and interpolation.

### 4. Technical Mechanism

#### 4.1 Pipeline
![Pipeline Figure](figures/fig02_pipeline.png)
- (1) The figure shows accelerated generation by sampling only a subsequence of timesteps, such as $\tau=[1,3]$, instead of visiting every intermediate state. (2) The key variable is the trajectory $\tau$, which controls the number of neural network evaluations used at sampling time.

#### 4.2 Architecture / Core Design
![Architecture Figure](figures/fig01_core_design.png)
- (1) The figure contrasts DDPM's Markovian inference model with DDIM's non-Markovian one: DDIM can connect a noisy state to $x\_0$ while preserving the same per-timestep marginals. (2) The key design choice is to reuse the same denoising model $\epsilon\_\theta$ and change the sampling process, not the training procedure.

#### 4.3 Core Equation
- The DDIM sampling update exposes the paper's central control knob:

$$
x_{t-1} = \sqrt{\alpha_{t-1}}\left(\frac{x_t-\sqrt{1-\alpha_t}\epsilon_\theta^{(t)}(x_t)}{\sqrt{\alpha_t}}\right) + \sqrt{1-\alpha_{t-1}-\sigma_t^2}\epsilon_\theta^{(t)}(x_t) + \sigma_t\epsilon_t
$$

- Variables:
  - $x\_t$: the current noisy sample at timestep $t$ (Sec 2 / Eq 3).
  - $x\_{t-1}$: the next sample after one reverse update (Sec 4.1 / Eq 12).
  - $\epsilon\_\theta^{(t)}(x\_t)$: the trained denoising network's noise prediction at timestep $t$ (Sec 4.1 / Eq 12).
  - $\alpha\_t$: the signal-retention schedule that defines each marginal $q(x\_t \mid x\_0)$ (Sec 2 / Eq 3).
  - $\sigma\_t$: the stochasticity control; $\sigma\_t=0$ gives the deterministic DDIM process (Sec 4.1).
  - $\epsilon\_t$: fresh Gaussian noise used only when the reverse process is stochastic (Sec 4.1 / Eq 12).

#### 4.4 Comparison: Others vs This Paper
The paper's claim is that diffusion sampling can be accelerated without retraining the denoising model. DDPM treats generation as a long reverse Markov chain, so skipping many steps usually damages quality. DDIM changes the inference family: it keeps the same training objective but defines non-Markovian reverse trajectories that can be much shorter (Sec 3 / Sec 4.2). Empirically, DDIM gives much better FID than stochastic DDPM-style sampling when the trajectory has only 10, 20, 50, or 100 steps, and the paper reports 10x to 50x wall-clock speedups compared with the original DDPM (Table 1 / Fig 4). The trade-off is that DDIM is still an iterative sampler; it reduces the bottleneck sharply but does not remove sequential denoising entirely.

#### 4.5 Qualitative Results
![Qualitative Results](figures/fig05_qualitative.png)
The qualitative figure shows DDIM's consistency property. Each column starts from the same initial latent $x\_T$, while rows use different numbers of sample timesteps. Even when the number of steps changes, the high-level identity of the generated sample stays similar: the same kind of object, room layout, or church structure remains recognizable.

This matters because it means $x\_T$ behaves like a meaningful latent code rather than disposable random noise. More steps improve detail and sharpness, but they do not usually rewrite the global content. That is why DDIM can support semantic interpolation and reconstruction more naturally than a highly stochastic DDPM sampling path.

### 5. Impact
DDIM shifted diffusion research from "can it generate well?" to "how few steps are really needed?" It became a standard fast sampler and a conceptual bridge between diffusion chains, implicit generative models, and probability-flow ODE views. Later samplers such as PNDM and DPM-Solver built directly on this acceleration perspective, treating diffusion sampling as a numerical trajectory problem. In practice, DDIM also became widely used in diffusion libraries because it can reuse existing DDPM-style checkpoints while offering a simple speed-quality knob.

### 6. Further Reading
[1] [Denoising Diffusion Probabilistic Models (2020)](https://arxiv.org/abs/2006.11239)<br>
Establishes the DDPM training objective and reverse denoising chain that DDIM reuses.<br>
[2] [Score-Based Generative Modeling through Stochastic Differential Equations (2021)](https://arxiv.org/abs/2011.13456)<br>
Unifies diffusion and score-based models with continuous-time reverse SDE and ODE views.<br>
[3] [Improved Denoising Diffusion Probabilistic Models (2021)](https://arxiv.org/abs/2102.09672)<br>
Improves DDPM likelihood and sampling efficiency through learned reverse-process variances.<br>
[4] [Pseudo Numerical Methods for Diffusion Models on Manifolds (2022)](https://arxiv.org/abs/2202.09778)<br>
Interprets DDIM as a numerical method and develops higher-quality pseudo linear multistep samplers.<br>
[5] [DPM-Solver: A Fast ODE Solver for Diffusion Probabilistic Model Sampling in Around 10 Steps (2022)](https://arxiv.org/abs/2206.00927)<br>
Designs a dedicated high-order ODE solver that can sample diffusion models in roughly 10 to 20 evaluations.<br>
[6] [Consistency Models (2023)](https://arxiv.org/abs/2303.01469)<br>
Pushes the acceleration question further by learning mappings that support one-step or few-step generation.<br>
