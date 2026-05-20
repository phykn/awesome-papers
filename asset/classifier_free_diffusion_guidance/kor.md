# Classifier-Free Diffusion Guidance

- **저자**: Jonathan Ho, Tim Salimans
- **학회/날짜**: arXiv 2022; 짧은 버전은 DGMs and Applications @ NeurIPS 2021
- **URL**: [https://arxiv.org/abs/2207.12598](https://arxiv.org/abs/2207.12598)
- **GitHub**: Not available

---

### 1. 배경
Conditional diffusion model은 target class나 condition 쪽으로 sampling을 밀어주면 더 선명하고 알아보기 쉬운 sample을 만들 수 있습니다. 이전의 강한 방법인 classifier guidance는 별도로 학습한 classifier의 gradient를 더해 이 효과를 만들었습니다. 하지만 이 extra classifier는 번거롭습니다. Noisy diffusion state에서 학습해야 하므로 일반 pretrained image classifier를 바로 쓸 수 없고, 전체 학습 pipeline도 복잡해집니다. 이 논문은 같은 fidelity-diversity control을 순수한 generative diffusion model만으로 만들 수 있는지 묻습니다.

### 2. 직관
Condition은 조향 신호라고 볼 수 있습니다. 일반 conditional diffusion model도 class label에 맞는 이미지로 가는 방향은 알고 있지만, 그 방향으로 약하게만 조향할 수 있습니다. Classifier-free guidance는 모델이 두 방향을 알게 만듭니다. 하나는 "이 condition에 맞는 이미지를 만들어라"이고, 다른 하나는 "그냥 일반 이미지를 만들어라"입니다. Sampling 때는 일반 방향을 일부 빼고 conditional direction을 키웁니다. 그래서 guidance scale을 올리면 sample은 더 선명하고 condition-specific해지지만, 다양성은 줄어듭니다.

### 3. 돌파구
핵심 돌파구는 classifier를 완전히 없애고, 하나의 diffusion network 안에 conditional behavior와 unconditional behavior를 같이 학습시키는 것입니다. 학습 중 condition $c$를 확률 $p\_{\mathrm{uncond}}$로 무작위 제거합니다. 그러면 같은 모델이 $\epsilon\_\theta(z\_\lambda,c)$와 $\epsilon\_\theta(z\_\lambda)$를 모두 배웁니다. Sampling 때는 이 두 예측을 선형 결합합니다. Guidance가 extra-model pipeline이 아니라 sampling rule 한 줄이 된 것입니다.

### 4. 기술적 메커니즘

#### 4.1 파이프라인
![Pipeline Figure](figures/fig_algorithms_pipeline.png)
- (1) 파이프라인은 먼저 condition dropout으로 하나의 diffusion model을 학습하고, sampling 때 각 denoising step에서 conditional prediction과 unconditional prediction을 섞습니다. (2) 핵심 제어 변수는 학습 중 condition을 지울 확률 $p\_{\mathrm{uncond}}$와 sampling 때 guidance strength를 정하는 $w$입니다.

#### 4.2 아키텍처 / 핵심 설계
![Core Design Figure](figures/fig02_guidance_toy.png)
- (1) Toy density 그림은 guidance가 분포를 어떻게 바꾸는지 보여줍니다. Guidance가 커질수록 probability mass는 각 conditional mode 안쪽으로 더 모이고, 다른 class와는 더 멀어집니다. (2) 핵심 설계 선택은 classifier를 학습하지 않고, conditional score와 unconditional score를 generative model 자체로 추정하는 것입니다.

#### 4.3 핵심 공식
- Classifier-free guided prediction은 conditional prediction과 unconditional prediction의 선형 결합입니다.

$$
\tilde{\epsilon}_\theta(z_\lambda,c) = (1+w)\epsilon_\theta(z_\lambda,c) - w\epsilon_\theta(z_\lambda)
$$

- 변수:
  - $z\_\lambda$: log-SNR level $\lambda$에서의 noisy diffusion state입니다.
  - $c$: ImageNet class label 같은 conditioning information입니다.
  - $\epsilon\_\theta(z\_\lambda,c)$: conditional noise prediction입니다.
  - $\epsilon\_\theta(z\_\lambda)$: null condition을 넣어 얻는 unconditional noise prediction입니다.
  - $w$: guidance strength입니다. 값이 커질수록 sample을 condition 쪽으로 더 강하게 밀어줍니다.
  - $\tilde{\epsilon}\_\theta(z\_\lambda,c)$: raw conditional prediction 대신 sampler가 사용하는 guided prediction입니다.

#### 4.4 비교: 다른 기술 vs 이 논문
이 논문의 주장은 guidance에 external classifier가 필요 없다는 것입니다. Classifier guidance는 sample fidelity를 높일 수 있지만, noisy-state classifier를 따로 학습하고 diffusion score에 classifier gradient를 섞어야 합니다. Classifier-free guidance는 extra model을 joint conditional/unconditional training과 sampling-time linear combination으로 대체합니다 (Algorithms 1 and 2). ImageNet 64 x 64와 128 x 128 실험은 classifier guidance와 비슷한 FID/IS tradeoff를 보여줍니다. 약한 guidance는 FID를 개선하고, 강한 guidance는 Inception Score를 올리지만 diversity를 줄입니다 (Tables 1 and 2 / Figs. 4 and 5). 단점은 naive sampling에서 step마다 diffusion model을 두 번 평가해야 하므로 속도가 느려질 수 있다는 점입니다.

#### 4.5 정성적 결과
![Qualitative Results](figures/fig03_imagenet_guidance.png)
정성적 그림은 128 x 128 ImageNet에서 왼쪽의 non-guided sample과 오른쪽의 classifier-free guided sample을 비교합니다. Guided sample은 더 class-specific하고 시각적으로 분명합니다. 고양이는 더 고양이답고, 개는 더 깔끔하며, 화산 이미지는 더 전형적인 화산처럼 보입니다.

이 그림은 knob의 비용도 보여줍니다. 강한 guidance는 색을 더 포화시키고 variation을 줄일 수 있습니다. 이는 논문이 정량적으로 보인 fidelity-diversity tradeoff와 같은 방향입니다.

### 5. 영향
Classifier-free guidance는 diffusion generation의 표준 제어 방식이 되었습니다. 중요한 이유는 단순하고, 모델 종류에 크게 묶이지 않으며, 별도 classifier가 필요 없기 때문입니다. 이후 text-to-image system은 같은 아이디어를 사용해 prompt가 sampling에 더 강하게 반영되도록 만들었습니다. 실무적으로 guidance scale은 diversity, prompt adherence, perceived sharpness를 직접 조절하는 가장 익숙한 diffusion control 중 하나가 되었습니다.

### 6. 후속 연구
[1] [Denoising Diffusion Probabilistic Models (2020)](https://arxiv.org/abs/2006.11239)<br>
Classifier-free guidance가 기반으로 삼는 DDPM framework와 noise-prediction training objective를 정립했습니다.<br>
[2] [Diffusion Models Beat GANs on Image Synthesis (2021)](https://arxiv.org/abs/2105.05233)<br>
Diffusion sampling에서 diversity와 fidelity를 조절하는 강한 baseline인 classifier guidance를 제안했습니다.<br>
[3] [GLIDE: Towards Photorealistic Image Generation and Editing with Text-Guided Diffusion Models (2021)](https://arxiv.org/abs/2112.10741)<br>
Guidance 아이디어를 text-conditioned diffusion과 image editing에 적용했습니다.<br>
[4] [High-Resolution Image Synthesis with Latent Diffusion Models (2022)](https://arxiv.org/abs/2112.10752)<br>
Diffusion을 latent space로 옮겼고, 이후 classifier-free guidance가 널리 쓰이는 기반이 되었습니다.<br>
[5] [Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding (2022)](https://arxiv.org/abs/2205.11487)<br>
Guidance strength가 sample quality와 text alignment에 중요한 대규모 text-to-image diffusion을 보여줬습니다.<br>
