# Wasserstein GAN
- **Authors**: Martin Arjovsky, Soumith Chintala, Léon Bottou
- **Venue/Date**: ICML 2017 (arXiv:1701.07875)
- **URL**: https://arxiv.org/abs/1701.07875
- **GitHub**: https://github.com/martinarjovsky/WassersteinGAN

## 1. Background
- The original GAN trains $G$ against a Jensen–Shannon (JS) divergence: when $p\_r$ and $p\_g$ live on low-dimensional manifolds with disjoint supports — the typical situation for image data — JS saturates to a constant $\log 2$ and its gradient vanishes. Training becomes a knife-edge act of keeping $D$ "good enough but not too good".
- The community's workaround — adding pixel-wide Gaussian noise so the supports overlap — visibly blurs samples and biases the maximum-likelihood estimate. A different *distance* between distributions was needed, one that stays smooth even when the supports don't touch.

## 2. Intuition
- Think of $p\_r$ and $p\_g$ as two piles of sand in the room. JS divergence asks a binary question: "is each grain at the right spot?" — when none are, the answer is always "no", and you learn nothing about which way to push. The Earth-Mover (Wasserstein) distance asks instead: "what is the minimum total distance I must transport sand to reshape one pile into the other?"
- That shipping-cost stays meaningful no matter how far apart the piles are, and it shrinks linearly as you slide one pile toward the other. So a loss built on it gives the generator a gradient that *points home* even before the two distributions begin to overlap.

## 3. Breakthrough
- The infimum form of the EM distance is intractable, but the **Kantorovich–Rubinstein duality** rewrites it as a *supremum* over 1-Lipschitz functions: $W(p\_r, p\_g) = \sup\_{\Vert f \Vert\_L \le 1} \mathbb{E}\_{x \sim p\_r}[f(x)] - \mathbb{E}\_{x \sim p\_g}[f(x)]$. That is exactly the shape of a discriminator loss — no $\log$, no sigmoid — and it can be approximated by a neural network.
- To enforce the Lipschitz constraint cheaply, the authors **clip the critic's weights to a small box** $[-c, c]^l$ after every update. Crude but effective: the parameter set is now compact, so $f\_w$ is automatically $K$-Lipschitz for some $K$ that depends only on the box, and the network can be trained *to optimality* without saturating.

## 4. Technical Mechanism

### 4.1 Pipeline
![Pipeline Figure](figures/fig01_pipeline.png)
- Reading the two panels side by side reveals the whole motivation. For parallel-lines distributions $p\_0$ and $p\_\theta$ (Example 1), the left panel plots $W(p\_r, p\_\theta)$ vs $\theta$ — a clean V whose slope is $\pm 1$ everywhere — while the right panel plots $\mathrm{JSD}$, flat at $\log 2$ except at the single point $\theta = 0$.
- Key variable: the *gradient* $\partial \rho / \partial \theta$. Wasserstein supplies one almost everywhere; JS supplies one nowhere — which is precisely why GAN training stalls when $D$ becomes too good.

### 4.2 Architecture / Core Design
![Architecture Figure](figures/alg01_architecture.png)
- The "architecture" is again a training loop, but with three differences from the original GAN: $D$ is renamed *critic* and outputs unbounded reals (no sigmoid); weights $w$ are clipped to $[-c, c]$ after every step (line 7); the optimizer is **RMSProp**, not momentum-based Adam, since the loss surface is non-stationary.
- Key design choice: $n\_{\text{critic}} = 5$ inner updates per generator step. Because the EM loss never saturates, training the critic *to optimality* gives a more reliable gradient — the opposite of the GAN folklore that warns against an "over-trained" discriminator.

### 4.3 Core Equation
- The practical WGAN objective — what is actually maximized at every critic step.

$$
\max\_{w \in \mathcal{W}} \, \mathbb{E}\_{x \sim p\_r}[f\_w(x)] - \mathbb{E}\_{z \sim p(z)}[f\_w(g\_\theta(z))]
$$

- Variables:
  - $f\_w$: critic neural network with weights $w$ constrained to a compact set $\mathcal{W} = [-c, c]^l$ (Eq 3, Algo 1).
  - $g\_\theta$: generator mapping latent $z$ to data space (Sec 1).
  - $p\_r$: real distribution; $p\_g$: distribution induced by $g\_\theta(z)$ (Sec 2).
  - $c$: weight-clipping threshold, fixed at $0.01$ (Algo 1 default).
  - $n\_{\text{critic}}$: critic updates per generator step, fixed at $5$ (Algo 1 default).

### 4.4 Comparison: Others vs This Paper
The authors argue WGAN cures three notorious GAN pathologies at once: vanishing gradients, mode collapse, and the architectural fragility that made DCGAN the only reliable recipe. The baseline limitation is structural — JS divergence is *flat* on disjoint manifolds, so $D$ either saturates or destabilizes $G$. WGAN replaces the divergence itself, optimizing an EM lower bound via Kantorovich–Rubinstein duality and enforcing the Lipschitz constraint with weight clipping. The mechanism is the critic loss in Eq 3; the evidence is two-fold. Figure 2 shows the critic converging to a *linear* function with clean gradients everywhere, while a GAN discriminator saturates to $0/1$ and provides none. Figure 3 shows the Wasserstein estimate decreasing monotonically and tracking sample quality — even on architectures (MLP, no-batchnorm DCGAN) where the standard GAN fails outright (Sec 4.2, Figs 5–7). The trade-offs are equally explicit: weight clipping is, in the authors' own words, "a clearly terrible way to enforce a Lipschitz constraint" — too small a $c$ vanishes gradients across deep nets, too large a $c$ slows convergence — and momentum-style optimizers can destabilize the critic, which is why RMSProp is preferred.

### 4.5 Qualitative Results
![Qualitative Results](figures/fig03_qualitative.png)
- Each subplot pairs the Wasserstein estimate (the critic's loss, blue curve) with bedroom samples drawn at matching iterations. The top row shows MLP and DCGAN generators trained with WGAN — both loss curves descend smoothly across $\sim$$6 \times 10^5$ iterations, and the inset samples sharpen in step with the curve.
- The bottom panel (MLP generator + MLP critic) is the most informative: training never converges, the loss never settles, and the samples remain noise. Crucially, you can *read this off the curve alone*. A GAN trained on the same setup gives you no such signal — its loss is uninformative throughout — so a practitioner has to inspect samples by eye every few thousand steps. WGAN turns the loss into the debugging dashboard the field had been missing.

## 5. Impact
- WGAN reframed adversarial training as Lipschitz-constrained optimal transport and made the loss curve *meaningful* for the first time, ending the era of staring at sample grids to gauge progress. Its principles fed directly into WGAN-GP (gradient penalty), spectral normalization, and the loss landscapes used by Progressive Growing of GANs and the early StyleGAN series.
- Beyond GANs, the paper helped popularize the integral-probability-metric viewpoint in deep learning, which now anchors evaluation (FID's underlying ideas, sliced Wasserstein) and surfaces in optimal-transport regularizers across domain adaptation, generative modeling, and even diffusion-model training stabilization.

## 6. Further Reading
[1] [Improved Training of Wasserstein GANs (2017)](https://arxiv.org/abs/1704.00028)<br>
WGAN-GP — replaces weight clipping with a gradient penalty on the critic, fixing capacity loss and making Adam usable again.<br>
[2] [Towards Principled Methods for Training Generative Adversarial Networks (2017)](https://arxiv.org/abs/1701.04862)<br>
The companion theoretical paper that formally diagnoses why JS-based GAN training suffers vanishing gradients on low-dimensional manifolds.<br>
[3] [Spectral Normalization for Generative Adversarial Networks (2018)](https://arxiv.org/abs/1802.05957)<br>
A drop-in Lipschitz constraint via per-layer spectral-norm division — competitive with WGAN-GP at far lower compute cost.<br>
[4] [f-GAN: Training Generative Neural Samplers using Variational Divergence Minimization (2016)](https://arxiv.org/abs/1606.00709)<br>
Generalizes the original GAN to arbitrary $f$-divergences — the natural foil for WGAN's integral-probability-metric viewpoint.<br>
[5] [Progressive Growing of GANs for Improved Quality, Stability, and Variation (2017)](https://arxiv.org/abs/1710.10196)<br>
Builds on the WGAN-GP loss to scale generation to $1024^2$ photorealistic faces, a direct lineage to StyleGAN.<br>
[6] [Generative Adversarial Nets (2014)](https://arxiv.org/abs/1406.2661)<br>
The original minimax-with-JS objective that WGAN explicitly diagnoses and replaces.<br>
