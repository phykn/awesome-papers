# Generating 3D Structures from a 2D Slice with GAN-Based Dimensionality Expansion

- **Authors**: Steve Kench, Samuel J. Cooper
- **Venue/Date**: Preprint - February 16, 2021 (arXiv:2102.07708)
- **URL**: [https://arxiv.org/abs/2102.07708](https://arxiv.org/abs/2102.07708)
- **GitHub**: [https://github.com/stke9/SliceGAN](https://github.com/stke9/SliceGAN)

---

### 1. 배경
재료의 물리적, 화학적 특성은 그 3차원 미세구조(microstructure)에 의해 크게 좌우됩니다. 하지만 X선 토모그래피(X-ray tomography)와 같은 고정밀 3차원 데이터셋을 얻는 과정은 시간이 오래 걸리고 비용이 많이 들며 해상도에 한계가 있습니다. 반면, SEM 이미지와 같은 2차원 현미경 사진(micrograph)은 얻기 쉽고 해상도가 높지만 물리 시뮬레이션에 필요한 3차원 깊이 정보가 부족합니다. 기존의 통계적 재구성 방식은 복잡하고 무작위가 아닌 위상(topology) 특징을 포착하는 데 한계가 있었으며, 이에 따라 2차원에서 3차원으로의 "차원 확장"을 수행할 수 있는 생성 모델의 필요성이 대두되었습니다.

### 2. 직관
복잡한 3차원 대리석 무늬 케이크(marble cake)를 직접 본 적 없이, 잘린 단면 사진들만 가지고 그 케이크를 똑같이 만들어야 한다고 상상해 보십시오. "SliceGAN"의 핵심 직관은 만약 생성된 3차원 케이크를 가로, 세로, 깊이 방향으로 어떻게 자르더라도 그 단면이 실제 케이크의 단면 사진과 통계적으로 구분되지 않는다면, 그 3차원 케이크는 실제 구조와 일치할 것이라는 점입니다. 단면을 완벽하게 재현함으로써 전체 부피를 학습하는 방식입니다.

### 3. 돌파구
SliceGAN의 핵심 돌파구는 생성기(Generator)와 판별기(Discriminator)의 차원을 분리한 것입니다. 생성기는 3차원 부피 데이터를 만들지만, 판별기는 오직 그 부피에서 추출된 2차원 슬라이스들만 검사합니다. 이를 통해 모델은 3차원 훈련 데이터 없이 오직 2차원 이미지 데이터만으로 3차원 부피를 생성하도록 학습될 수 있습니다. 여러 평면에서 2차원 통계적 일관성을 강제함으로써, 모델은 재료 구조상 물리적으로 타당한 방식으로 세 번째 차원을 효과적으로 "상상"해 냅니다.

### 4. 기술적 메커니즘

#### 4.1 파이프라인
![Pipeline Figure](figures/fig01_pipeline.png)
- 파이프라인은 잠재 벡터 (latent vector) $z$에서 시작하며, 3차원 생성기 ($G$) 는 이를 3차원 부피 샘플 $f$로 변환합니다. 이 부피를 $x$, $y$, $z$축을 따라 슬라이싱하여 2차원 이미지를 생성하고, 2차원 판별기 ($D$) 는 이를 실제 훈련용 이미지와 비교하여 피드백을 제공합니다.
- 주요 모듈: (1) 부피 합성을 위한 3차원 생성기 $G$, (2) 3차원과 2차원의 간극을 메우는 슬라이싱(Slicing) 연산.

#### 4.2 아키텍처 / 핵심 설계
![Architecture Figure](figures/tab01_architecture.png)
- 생성기에서는 1차원의 잠재 벡터를 $64^3$ 크기의 부피로 확장하기 위해 3차원 전치 컨볼루션(transpose convolution)을 사용하며, 판별기에서는 슬라이스를 평가하기 위해 표준 2차원 컨볼루션을 사용합니다.
- 핵심 설계: 입력 $z$의 공간 차원을 $1 \times 1 \times 1$이 아닌 $4 \times 4 \times 4$로 설정하여 생성된 부피 전반에 걸쳐 균일한 정보 밀도를 보장하고 가장자리 아티팩트(edge artifacts)를 방지했습니다.

#### 4.3 핵심 방정식
- **선택 기준**: 안정적인 학습과 고품질 합성을 보장하기 위해 사용된 Gradient Penalty가 포함된 Wasserstein GAN 손실 함수(WGAN-GP)를 선택했습니다.
- **방정식**:

$$ L\_D = \mathbb{E}[D(G(z)\_s)] - \mathbb{E}[D(r)] + \lambda \mathbb{E}[(\Vert \nabla\_{\hat{x}} D(\hat{x}) \Vert\_2 - 1)^2] $$

- 이 식은 가짜 슬라이스와 실제 이미지 분포 사이의 "거리"를 측정합니다.
- **변수 설명**: 
    - $G(z)\_s$: 생성된 3차원 부피에서 추출된 2차원 슬라이스 (3페이지).
    - $r$: 실제 2차원 훈련용 이미지 (3페이지).
    - $\lambda$: 학습 안정화를 위한 Gradient Penalty 계수.

#### 4.4 비교: 기존 방식 vs 본 논문
SliceGAN은 장거리 연결성 및 복잡한 상(phase)을 포착하는 데 있어 기존의 확률론적 또는 상관관계 기반 재구성 방식보다 훨씬 뛰어난 성능을 보입니다. 3차원 훈련 데이터가 필수적인 표준 3차원 GAN과 달리, 이 방식은 널리 보급된 2차원 현미경 사진만으로 작동합니다. 논문에서는 학습 완료 후 SliceGAN이 수 초 만에 $10^8$개의 복셀(voxel) 부피를 생성할 수 있음을 보여주었으며, 이는 기존 물리 시뮬레이션 대비 약 $10^5$배의 속도 향상을 의미합니다. 또한 다결정 입자, 세라믹 섬유, 배터리 전극 등 다양한 재료에 대해 견고한 성능을 입증했습니다(섹션 5.2 / 그림 3).

#### 4.5 정성적 결과
![Qualitative Results](figures/fig03_qualitative.png)
정성적 결과는 단순한 입자 구조(행 A)부터 복잡한 다상 배터리 분리막 재료(행 D)에 이르기까지 다양한 미세구조가 성공적으로 재구성되었음을 보여줍니다. 왼쪽에서 오른쪽으로 실물 2차원 이미지, 생성된 3차원 부피, 그리고 다양한 각도에서 본 슬라이스들이 나열되어 있습니다. 특히 45도 각도 슬라이스(가장 오른쪽 열)는 생성기가 단순히 축 방향 데이터를 외운 것이 아니라 일관된 3차원 표현을 학습했음을 증명합니다. 비록 행 A의 입자 경계에서 원본에는 없는 미세한 곡률이 관찰되기도 하지만, 모든 재료 유형에서 전체적인 위상 연결성은 매우 실제와 가깝게 유지되었습니다(그림 3).

### 5. 영향력
SliceGAN은 재료 과학계에 강력한 도구를 제공하여, 단순한 2차원 관찰만으로 응력 분석이나 유체 흐름과 같은 물리 기반 시뮬레이션을 위한 대표적인 3차원 부피를 생성할 수 있게 합니다. 이는 고해상도 2차원 데이터와 3차원 부피 분석의 필요성 사이의 간극을 메움으로써, 차세대 에너지 재료 및 복합 재료의 발견과 최적화를 가속화할 잠재력을 가지고 있습니다.

### 6. 추가 읽을거리
[1] [Super-resolution of multiphase materials by combining complementary 2D and 3D image data using generative adversarial networks (2021)](https://arxiv.org/abs/2110.11281)<br>
2D와 3D 정보를 결합하여 미세구조의 해상도를 높이는 후속 연구입니다.

[2] [Micro3Diff: Multi-plane denoising diffusion-based dimensionality expansion (2023)](https://arxiv.org/abs/2308.14035)<br>
확산 모델(Diffusion Model)을 사용한 최신 2D-to-3D 재구성 기법입니다.

[3] [SliceGAN Github Issues/Discussions](https://github.com/stke9/SliceGAN)<br>
실제 구현 팁과 후속 커뮤니티 연구 내용.
