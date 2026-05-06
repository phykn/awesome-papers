# Generative Adversarial Nets
- **저자**: Ian J. Goodfellow, Jean Pouget-Abadie, Mehdi Mirza, Bing Xu, David Warde-Farley, Sherjil Ozair, Aaron Courville, Yoshua Bengio
- **학회/일자**: NeurIPS 2014 (arXiv:1406.2661)
- **URL**: https://arxiv.org/abs/1406.2661
- **GitHub**: https://github.com/goodfeli/adversarial

## 1. 배경
- 기존의 심층 생성 모델인 볼츠만 머신(Boltzmann machine)이나 심층 신뢰망(deep belief net)은 분배함수(partition function)가 다루기 까다로워 학습과 표본 추출 모두 느린 MCMC에 의존했고, NADE·RNADE 같은 명시적 밀도(explicit density) 모델은 인수분해 가능한 우도로 표현 범위가 제한됐습니다.
- 모두 데이터 확률을 직접 적어 두고 최적화하려 했기 때문에 변분 하한(variational bound)이나 대조발산(contrastive divergence) 같은 근사가 강제됐습니다. 우도 평가 자체를 거치지 않고 곧바로 표본을 생성할 수 있는 새로운 경로가 필요했습니다.

## 2. 직관
- 위조지폐범(생성자 ($G$))이 가짜 돈을 찍어 내고, 형사(판별자 ($D$))가 가짜를 잡아내려 한다고 상상해 봅시다. 매 라운드마다 형사는 결함을 더 잘 찾아내고, 위조지폐범은 새로운 형사를 속이도록 더 정교해집니다.
- 균형점에서는 가짜가 진짜와 통계적으로 구분 불가능해져 형사는 동전 던지기 수준으로 떨어집니다. "진짜 돈이 어떻게 생겼는지"를 명시적으로 적어 둔 사람은 아무도 없는데도, 모델은 두 네트워크의 경쟁만으로 그 분포를 학습한 셈입니다.

## 3. 돌파구
- 다루기 어려운 우도를 **학습되는**(learned) 손실로 갈아 끼웁니다. $\log p\_{\text{model}}(x)$를 최대화하는 대신, 두 네트워크를 맞붙여 게임의 안장점이 정확히 $p\_g = p\_{\text{data}}$가 되도록 학습합니다.
- 이로써 밀도 추정 문제가 역전파(backpropagation)가 자연스럽게 처리할 수 있는 이진 분류 문제로 바뀌고, 생성자는 자신의 확률 질량을 한 번도 계산하지 않고도 학습 신호를 받을 수 있게 됩니다.

## 4. 기술 메커니즘

### 4.1 파이프라인
![Pipeline Figure](figures/fig01_pipeline.png)
- 패널을 (a)→(d) 순서로 따라가면 학습 진행이 보입니다. 점선 곡선은 $p\_{\text{data}}$, 실선 녹색은 $p\_g$, 파란 점선은 판별자 ($D$)이고, $z$에서 $x$로 향하는 화살표는 잠재 사전분포를 데이터 공간으로 밀어 넣는 ($G$)를 나타냅니다. 학습이 진행될수록 $p\_g$가 $p\_{\text{data}}$와 겹치고, ($D$)는 모든 점에서 $\tfrac{1}{2}$로 수렴합니다.
- 핵심 변수: 판별자 출력 $D(x) \in [0,1]$이 생성자가 보는 **유일한 신호**(only signal)입니다. 가짜 표본을 통해 흐르는 그래디언트가 ($G$)를 학습시킵니다.

### 4.2 아키텍처 / 핵심 설계
![Architecture Figure](figures/alg01_architecture.png)
- 여기서의 "아키텍처"는 네트워크 도식이 아니라 학습 루프입니다. 생성자 1회 갱신마다 판별자를 $k$회 갱신하며, 양쪽 모두 실제 표본 $x$와 노이즈 $z$로 구성된 미니배치에 일반 SGD를 적용합니다.
- 핵심 설계 선택: 비대칭 ($k{:}1$) 스케줄로 ($D$)를 최적해 근방에 유지해 ($G$)를 위한 그래디언트가 정보성을 잃지 않도록 합니다. 또한 학습 초반의 그래디언트 소실을 피하기 위해 ($G$)는 실제로는 $\log(1 - D(G(z)))$를 최소화하는 대신 $\log D(G(z))$를 최대화합니다.

### 4.3 핵심 수식
- 두 플레이어가 벌이는 미니맥스(minimax) 가치 함수입니다. 이후의 모든 GAN 변종은 이 목적함수의 변형입니다.

$$
\min\_G \max\_D V(D, G) = \mathbb{E}\_{x \sim p\_{\text{data}}(x)}[\log D(x)] + \mathbb{E}\_{z \sim p\_z(z)}[\log(1 - D(G(z)))]
$$

- 변수:
  - $D(x)$: $x$가 진짜일 확률에 대한 판별자 추정값 (Eq 1).
  - $G(z)$: 노이즈 표본을 데이터 공간으로 보내는 생성자 (Eq 1).
  - $p\_{\text{data}}$: 실제 데이터 분포, $p\_g$: $G(z)$가 만들어 내는 암시적 분포 (Sec 3).
  - $p\_z$: 잠재 변수 $z$에 대한 고정된 노이즈 사전분포 (예: 균일분포·가우시안) (Eq 1).

### 4.4 비교: 기존 vs 본 논문
저자들은 적대적(adversarial) 학습이 기존 생성 모델의 약점을 모두 우회한다고 주장합니다. 볼츠만 머신은 학습과 표본 추출 양쪽에서 MCMC 사슬이 필요하고, 변분 오토인코더(VAE)는 학습 분포를 편향시키는 하한을 최적화합니다. GAN은 $p\_g$를 명시적으로 표현하지 않는다는 점에서 다릅니다. 네트워크는 표본 추출기로만 정의되고, 손실은 다른 네트워크가 공급합니다. 이 메커니즘은 식 1의 미니맥스 게임이며, 그 전역 최적점이 정확히 $p\_g = p\_{\text{data}}$임이 해석적으로 증명됩니다 (Sec 4.1). 실험적으로는 더 선명한 표본과 MNIST/TFD/CIFAR-10에서 경쟁력 있는 Parzen 로그우도를 보여 줍니다 (Table 1 / Fig 2). 잘 알려진 트레이드오프도 있습니다. 명시적 밀도가 없고, 유한 용량 네트워크에서 수렴 보장이 없으며, ($k{:}1$) 균형이 무너지면 ($G$)가 일부 모드에 붕괴(mode collapse)할 수 있습니다.

### 4.5 정성적 결과
![Qualitative Results](figures/fig02_qualitative.png)
- 각 패널의 왼쪽 열들은 생성된 표본이고, 오른쪽 노란 박스는 그 표본과 가장 가까운 **학습 데이터 표본**(nearest training example)입니다. 모델이 데이터를 외운 것이 아니라 보간(interpolation)하고 있음을 눈으로 확인하기 위함입니다. (a) MNIST 숫자는 또렷하면서도 스타일이 다양하고, (b) Toronto Face Database 얼굴은 어떤 학습 이미지와도 일치하지 않는 새로운 자세와 조명을 포착합니다.
- (c) 완전 연결(fully-connected) 생성자로 만든 CIFAR-10은 흐릿한 저주파 색 덩어리로 무너져 자연 이미지에서의 한계를 드러냅니다. (d) 합성곱(convolutional) ($G/D$) 쌍은 훨씬 더 텍스처가 살아 있는 동물 같은 표본을 생성하는데, 이듬해 등장한 DCGAN의 전면 합성곱 설계가 왜 곧바로 다음 도약이 되었는지를 미리 보여 줍니다.

## 5. 영향
- GAN은 심층 생성 모델링을 학습 가능한 2-플레이어 게임으로 재정의하며 거대한 연구 흐름을 열었습니다. DCGAN, Conditional GAN, WGAN, CycleGAN, BigGAN, StyleGAN, 그리고 현대의 이미지·비디오 합성 파이프라인이 모두 이 목적함수에서 출발합니다.
- 이미지 너머로도 적대적 원리는 표현 학습, 도메인 적응(domain adaptation)을 재편했고, 결국 확산(diffusion) 모델의 학습·평가에까지 영향을 미쳤습니다 (FID는 판별자 계열 분류기 위에서 계산됩니다).

## 6. 더 읽을거리
[1] [Unsupervised Representation Learning with Deep Convolutional Generative Adversarial Networks (2015)](https://arxiv.org/abs/1511.06434)<br>
DCGAN — GAN 이미지를 일관되게 선명하게 만든 전면 합성곱 아키텍처와 학습 노하우.<br>
[2] [Conditional Generative Adversarial Nets (2014)](https://arxiv.org/abs/1411.1784)<br>
($G$)와 ($D$) 모두에 조건 입력 $y$를 추가해 클래스 조건부·이미지 변환 생성을 가능하게 합니다.<br>
[3] [Wasserstein GAN (2017)](https://arxiv.org/abs/1701.07875)<br>
Jensen–Shannon 목적함수를 Earth-Mover 거리로 교체해 그래디언트 소실과 모드 붕괴를 완화합니다.<br>
[4] [A Style-Based Generator Architecture for Generative Adversarial Networks (2018)](https://arxiv.org/abs/1812.04948)<br>
StyleGAN — 스타일·콘텐츠를 분리한 제어로 사실적 얼굴 합성을 현재 수준까지 끌어올린 분기점.<br>
[5] [Auto-Encoding Variational Bayes (2013)](https://arxiv.org/abs/1312.6114)<br>
같은 시기에 등장한 VAE — GAN의 가장 자주 비교되는 "명시적 밀도" 대안.<br>
