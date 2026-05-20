# High-Resolution Image Synthesis with Latent Diffusion Models

- **저자**: Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, Björn Ommer
- **학회/날짜**: CVPR 2022
- **URL**: [https://arxiv.org/abs/2112.10752](https://arxiv.org/abs/2112.10752)
- **GitHub**: [https://github.com/CompVis/latent-diffusion](https://github.com/CompVis/latent-diffusion)

---

### 1. 배경
Diffusion model은 이미 높은 품질의 이미지 생성을 보여주고 있었습니다. 하지만 대부분 픽셀 공간에서 직접 잡음 제거를 했기 때문에 비용이 컸습니다. 고해상도 이미지는 픽셀 수가 많고, 샘플링 단계마다 큰 신경망을 전체 해상도에 적용해야 합니다. 학습은 수백 GPU-day를 요구할 수 있고, 추론도 많은 순차 잡음 제거 단계를 거쳐야 했습니다. 핵심 질문은 diffusion의 품질과 조건 제어 능력을 유지하면서 픽셀 공간 생성의 비용을 줄일 수 있느냐였습니다.

### 2. 직관
LDM은 이미지를 바로 큰 캔버스에 그리는 대신, 먼저 작은 설계도 공간에서 그림을 만든 뒤 마지막에 렌더링하는 방식입니다. 이미지 전체 픽셀을 diffusion model이 직접 다루게 하지 않고, autoencoder가 이미지를 latent code로 압축합니다. Diffusion model은 이 latent code에서 잡음을 제거합니다. 이 공간은 더 작지만 시각적으로 중요한 내용은 유지합니다. 마지막에는 decoder가 잡음이 제거된 latent를 다시 픽셀 이미지로 바꿉니다. 즉 의미 있는 생성 과정은 diffusion이 맡고, 세부 픽셀 복원은 autoencoder가 맡습니다.

### 3. 돌파구
핵심 돌파구는 압축률과 품질 사이의 좋은 지점을 찾은 것입니다. 너무 강한 압축은 세부 정보를 잃고, 픽셀 공간 diffusion은 눈에 잘 보이지 않는 신호까지 모두 모델링하느라 비쌉니다. LDM은 perceptual autoencoder를 학습한 뒤, 그 latent space에서 diffusion을 실행합니다. 그래서 의미 없는 픽셀 수준 중복은 줄이고, 고품질 합성에 필요한 구조는 남깁니다. 여기에 cross-attention conditioning을 추가해 같은 latent diffusion backbone으로 text, layout, semantic map, inpainting, super-resolution을 다룰 수 있게 했습니다.

### 4. 기술적 메커니즘

#### 4.1 파이프라인
![Pipeline Figure](figures/fig03_conditioning_architecture.png)
- (1) 파이프라인은 세 단계입니다. 이미지 $x$를 encoder $E$로 latent space에 넣고, denoising U-Net이 latent variable $z\_t$를 처리한 뒤, decoder $D$가 최종 latent를 다시 이미지로 복원합니다. (2) 핵심 변수는 $x\_t$가 아니라 $z\_t$입니다. Diffusion은 압축된 latent grid에서 일어나고, 최종 픽셀 복원은 decoder가 담당합니다.

#### 4.2 아키텍처 / 핵심 설계
![Core Design Figure](figures/fig02_compression.png)
- (1) 이 그림은 latent space가 왜 유용한지 보여줍니다. 이미지의 많은 bit는 사람이 거의 느끼지 못하는 세부 정보에 쓰이지만, 의미 내용은 perceptual compression 뒤에도 남습니다. (2) LDM은 계산량을 줄이면서도 realistic image synthesis에 필요한 정보를 보존하는 압축 지점을 선택합니다.

#### 4.3 핵심 공식
- LDM objective는 DDPM의 noise-prediction loss를 픽셀 공간이 아니라 autoencoder latent space로 옮긴 것입니다.

$$
L_{\mathrm{LDM}} := \mathbb{E}_{E(x), \epsilon \sim \mathcal{N}(0,1), t}\left[\left\|\epsilon - \epsilon_\theta(z_t,t)\right\|_2^2\right]
$$

- 변수:
  - $x$: 학습 데이터의 원본 이미지입니다.
  - $E(x)$: encoder output이며, 깨끗한 latent representation $z$로 사용됩니다.
  - $z\_t$: diffusion timestep $t$에서의 noisy latent입니다.
  - $\epsilon$: forward diffusion 과정에서 더해지는 Gaussian noise입니다.
  - $\epsilon\_\theta(z\_t,t)$: latent space에서 U-Net이 예측한 noise입니다.
  - $D(z)$: denoised latent를 픽셀 이미지로 바꾸는 decoder입니다.

#### 4.4 비교: 다른 기술 vs 이 논문
Pixel-space DDPM은 이미지를 직접 모델링합니다. 단순하고 표현력은 좋지만, 모든 잡음 제거 단계가 이미지 해상도에서 실행되기 때문에 비쌉니다. GAN 기반 autoencoder는 이미지를 효율적으로 압축할 수 있지만, diffusion의 안정적인 학습과 반복적 refinement를 제공하지는 않습니다. LDM은 둘을 결합합니다. Autoencoder는 perceptual compression을 맡고, diffusion은 압축된 latent space에서 generative modeling을 맡습니다. 그래서 pixel diffusion보다 속도-품질 tradeoff가 좋고, 단순 압축 모델보다 샘플 품질과 조건 제어 유연성이 강합니다.

#### 4.5 정성적 결과
![Qualitative Results](figures/fig04_samples.png)
정성적 결과는 latent model이 흐릿한 sketch만 복원하는 것이 아님을 보여줍니다. 얼굴, 교회, 침실, ImageNet object가 256 x 256 해상도에서 세부 묘사를 갖고 생성됩니다. 이는 매우 중요합니다. Latent compression이 너무 강하면 고주파 현실감이 사라질 수 있기 때문입니다. 이 그림은 적절히 선택한 latent space가 계산 낭비를 줄이면서도 고품질 생성에 충분한 정보를 남긴다는 논문의 중심 주장을 뒷받침합니다.

### 5. 영향
LDM은 현대 text-to-image system의 핵심 설계 패턴이 되었습니다. 가장 큰 교훈은 diffusion이 반드시 픽셀 공간에서 모든 modeling capacity를 써야 하는 것은 아니라는 점입니다. Perceptual compression과 생성 과정의 잡음 제거를 분리함으로써 고해상도 diffusion을 더 실용적으로 만들었고, text나 구조화된 condition을 넣기도 쉬워졌습니다. 이 아이디어는 Stable Diffusion 계열에 직접적인 기반이 되었고, 공개 고해상도 diffusion model을 일반적인 하드웨어에서도 다룰 수 있게 만들었습니다.

### 6. 후속 연구
[1] [Denoising Diffusion Probabilistic Models (2020)](https://arxiv.org/abs/2006.11239)<br>
LDM이 latent space 안에서 재사용하는 DDPM 학습 목적식을 정립했습니다.<br>
[2] [Denoising Diffusion Implicit Models (2020)](https://arxiv.org/abs/2010.02502)<br>
Latent diffusion checkpoint와 자주 함께 쓰이는 deterministic 및 accelerated diffusion sampling을 제안했습니다.<br>
[3] [GLIDE: Towards Photorealistic Image Generation and Editing with Text-Guided Diffusion Models (2021)](https://arxiv.org/abs/2112.10741)<br>
LDM이 효율적인 고해상도 경로로 자리 잡기 전, text-guided diffusion의 강한 성능을 보여줬습니다.<br>
[4] [Hierarchical Text-Conditional Image Generation with CLIP Latents (2022)](https://arxiv.org/abs/2204.06125)<br>
CLIP latent prediction과 image decoding을 계층적으로 결합한 text-to-image generation 접근입니다.<br>
[5] [Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding (2022)](https://arxiv.org/abs/2205.11487)<br>
대형 language encoder가 text-conditioned diffusion generation에 얼마나 중요한지 보여줬습니다.<br>
[6] [Classifier-Free Diffusion Guidance (2022)](https://arxiv.org/abs/2207.12598)<br>
제어 가능하고 고품질인 diffusion sampling에서 핵심이 된 guidance 방법을 정리했습니다.<br>
