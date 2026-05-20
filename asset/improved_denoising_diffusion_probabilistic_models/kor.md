# Improved Denoising Diffusion Probabilistic Models

- **저자**: Alex Nichol, Prafulla Dhariwal
- **학회/날짜**: arXiv 2021
- **URL**: [https://arxiv.org/abs/2102.09672](https://arxiv.org/abs/2102.09672)
- **GitHub**: [https://github.com/openai/improved-diffusion](https://github.com/openai/improved-diffusion)

---

### 1. 배경
DDPM은 diffusion model이 고품질 이미지를 만들 수 있음을 보였지만, 두 가지 실무 문제가 남아 있었습니다. 첫째, likelihood가 강한 likelihood 기반 모델과 경쟁하기에는 부족했습니다. 둘째, 생성에는 긴 역방향 잡음 제거 체인이 필요했기 때문에 샘플링이 느렸습니다. 원래 DDPM은 역방향 분산도 고정했습니다. 이는 샘플 품질에는 충분했지만 likelihood와 빠른 샘플링에는 한계가 있었습니다. 이 논문은 완전히 새 모델 계열을 만들지 않고, diffusion 과정의 작은 변경만으로 얼마나 개선할 수 있는지 묻습니다.

### 2. 직관
DDPM을 수천 개의 작은 지시문으로 이루어진 긴 이미지 복원 레시피라고 생각해 보세요. 원래 레시피는 각 역방향 단계가 얼마나 불확실해야 하는지를 미리 정해 둡니다. Improved DDPM은 그 불확실성의 일부를 모델이 직접 배우게 합니다. 그래서 샘플링 때 더 크고 잘 보정된 단계를 밟을 수 있습니다. 또한 시간에 따라 노이즈를 넣는 방식도 바꿉니다. 유용한 신호를 너무 일찍 망가뜨리지 않고, cosine schedule로 오염을 더 고르게 퍼뜨립니다. 결과적으로 같은 기본 레시피를 쓰되, 단계 크기와 시간표를 더 잘 고른 셈입니다.

### 3. 돌파구
핵심 돌파구는 세 가지 단순한 엔지니어링 변경만으로 DDPM을 훨씬 실용적으로 만든 것입니다. 모델은 알려진 두 분산 경계 사이를 안정적으로 보간해 역방향 분산을 학습합니다. 학습에는 hybrid objective를 사용합니다. 이 목적식은 단순화된 DDPM 손실의 강한 샘플 품질을 유지하면서도, 분산 예측 머리에 변분 학습 신호를 줍니다. 또한 linear noise schedule을 cosine schedule로 바꿔, 뒤쪽 diffusion step이 낭비되는 일을 줄입니다. 이 조합은 likelihood를 개선하고, 훨씬 적은 샘플링 단계에서도 높은 품질을 유지하게 합니다.

### 4. 기술적 메커니즘

#### 4.1 파이프라인
![Pipeline Figure](figures/fig03_cosine_pipeline.png)
- (1) 이 그림은 linear schedule과 cosine schedule에서 latent image가 어떻게 망가지는지 비교합니다. Cosine schedule은 뒤쪽 timestep을 너무 빨리 순수 노이즈로 만들지 않고, 유용한 이미지 구조를 더 오래 유지합니다. (2) 핵심 변수는 $\bar{\alpha}\_t$입니다. 이는 timestep $t$에서 원래 신호가 얼마나 남는지를 정합니다.

#### 4.2 아키텍처 / 핵심 설계
![Core Design Figure](figures/fig05_cosine_schedule.png)
- (1) schedule 그림은 같은 설계 선택을 수치적으로 보여줍니다. Cosine schedule은 linear schedule보다 신호를 더 부드럽게 줄입니다. (2) 핵심 설계는 DDPM의 잡음 제거 구조를 거의 유지하면서, diffusion 과정 자체를 더 좋게 만드는 것입니다.

#### 4.3 핵심 공식
- 핵심 분산 parameterization은 두 자연스러운 역방향 분산 경계 사이를 학습된 값으로 보간합니다.

$$
\Sigma_\theta(x_t,t) = \exp\left(v\log\beta_t + (1-v)\log\tilde{\beta}_t\right)
$$

- 변수:
  - $x\_t$: timestep $t$에서의 noisy sample입니다.
  - $\Sigma\_\theta(x\_t,t)$: 모델이 학습하는 역방향 과정의 분산입니다.
  - $v$: 두 분산 경계 사이를 보간하기 위해 모델이 출력하는 값입니다.
  - $\beta\_t$: forward process에서 timestep $t$에 더하는 노이즈 분산입니다.
  - $\tilde{\beta}\_t$: $x\_0$를 알고 있을 때의 정확한 역방향 posterior variance입니다.
  - $t$: 잡음 제거 예측과 분산 예측이 함께 사용하는 diffusion step입니다.

#### 4.4 비교: 다른 기술 vs 이 논문
이 논문의 주장은 DDPM이 작은 과정 수준 변경만으로 더 빠르고 likelihood 경쟁력 있는 모델이 될 수 있다는 것입니다. 원래 DDPM은 역방향 분산을 고정하고 linear noise schedule을 사용했습니다. 샘플 품질은 좋았지만 likelihood와 샘플링 효율에는 개선 여지가 있었습니다. Improved DDPM은 분산을 학습하고, hybrid objective를 쓰며, cosine schedule을 도입합니다 (섹션 3.1 / 섹션 3.2). 실험에서는 baseline보다 ImageNet 64 x 64 likelihood가 좋아지고, compute가 늘 때 성능이 부드럽게 scale하며, 충분히 학습된 모델은 약 100 sampling step만으로 거의 최적 FID에 도달합니다 (Fig. 8). 단점은 순수 VLB 최적화가 likelihood를 더 개선할 수 있지만 FID를 해치는 경향이 있어, 논문은 대체로 hybrid objective를 선호한다는 점입니다.

#### 4.5 정성적 결과
![Qualitative Results](figures/fig09_imagenet_samples.png)
정성적 그림은 hybrid objective 모델이 250 sampling step으로 만든 class-conditional ImageNet 64 x 64 sample을 보여줍니다. 새, 개, 오리, 도롱뇽 등 여러 class가 각기 다른 형태와 질감을 갖고 나타납니다. 이는 논문의 precision-recall 주장과도 맞습니다. Diffusion model은 일부 mode만 날카롭게 만드는 것이 아니라, 목표 분포를 넓게 덮을 수 있습니다.

이 그림이 중요한 이유는 원래 DDPM의 긴 체인보다 빠른 sampler에서 나온 결과이기 때문입니다. 즉 개선점은 likelihood 숫자에만 머무르지 않습니다. 학습된 분산과 개선된 과정이 샘플링 비용을 줄이면서도 눈에 보이는 이미지 품질을 유지한다는 것을 보여줍니다.

### 5. 영향
Improved DDPM은 diffusion을 유망하지만 느린 이미지 생성기에서 더 실용적이고 확장 가능한 modeling recipe로 바꿨습니다. Learned variance, hybrid objective, cosine schedule, step respacing은 이후 diffusion codebase의 표준 구성요소가 되었습니다. 또한 이 논문은 diffusion과 GAN을 비교할 때 FID만이 아니라 precision과 recall도 함께 보게 만들었습니다. 이후 고품질 diffusion system은 이 교훈을 이어받습니다. 더 큰 네트워크만큼이나 schedule과 샘플링 parameterization도 중요합니다.

### 6. 후속 연구
[1] [Denoising Diffusion Probabilistic Models (2020)](https://arxiv.org/abs/2006.11239)<br>
이 논문이 learned variance, schedule 변경, hybrid objective로 개선하는 기본 DDPM 레시피를 정립했습니다.<br>
[2] [Denoising Diffusion Implicit Models (2020)](https://arxiv.org/abs/2010.02502)<br>
Non-Markovian reverse trajectory를 통해 diffusion sampling을 빠르게 만드는 다른 경로를 제시했습니다.<br>
[3] [Score-Based Generative Modeling through Stochastic Differential Equations (2021)](https://arxiv.org/abs/2011.13456)<br>
Diffusion model을 연속시간 score-based SDE 및 ODE sampling 관점과 연결했습니다.<br>
[4] [Diffusion Models Beat GANs on Image Synthesis (2021)](https://arxiv.org/abs/2105.05233)<br>
Improved diffusion 아이디어에 architecture 변경과 classifier guidance를 더해 ImageNet 생성 품질을 강화했습니다.<br>
[5] [High-Resolution Image Synthesis with Latent Diffusion Models (2022)](https://arxiv.org/abs/2112.10752)<br>
Diffusion을 autoencoder latent space로 옮겨 고해상도 생성 비용을 줄였습니다.<br>
[6] [Classifier-Free Diffusion Guidance (2022)](https://arxiv.org/abs/2207.12598)<br>
Classifier guidance를 조건부/무조건부 score mixing으로 대체하는 더 단순한 guidance 규칙을 제안했습니다.<br>
