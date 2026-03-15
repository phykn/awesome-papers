---
title: 3D Gaussian Splatting for Real-Time Radiance Field Rendering
authors: Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, George Drettakis
venue: SIGGRAPH 2023
url: https://arxiv.org/abs/2308.04079
github: https://github.com/graphdeco-inria/gaussian-splatting
---

# 3D Gaussian Splatting for Real-Time Radiance Field Rendering

- **저자**: Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, George Drettakis
- **발표 학회/날짜**: SIGGRAPH 2023 / 2023년 8월
- **URL**: [https://arxiv.org/abs/2308.04079](https://arxiv.org/abs/2308.04079)
- **GitHub**: [https://github.com/graphdeco-inria/gaussian-splatting](https://github.com/graphdeco-inria/gaussian-splatting)

---

### 1. 배경
기존의 뉴럴 래디언스 필드(NeRF)는 밀도와 색상을 신경망(MLP)으로 표현하며 3D 장면 재구성의 혁명을 일으켰습니다. 하지만 NeRF는 렌더링 시 픽셀당 수천 번의 신경망 쿼리가 필요해 실시간 렌더링이 매우 어렵다는 치명적인 단점이 있었습니다. 최근의 Instant-NGP나 Plenoxels 같은 방식들이 격자(Grid) 구조를 통해 속도를 개선했지만, 복잡하고 넓은 장면의 미세한 디테일이나 배경을 표현하는 데는 여전히 한계가 있었습니다. 즉, '최상의 화질'과 '실시간 성능' 사이의 간극을 메울 새로운 접근법이 절실했습니다.

### 2. 직관적 이해
당신이 3D 장면을 그리는 화가라고 상상해 보세요. 3D 격자의 모든 점을 색으로 채우거나(복셀), 복잡한 수학 공식 하나로 전체 장면을 설명하려(NeRF) 애쓰는 대신, 부드럽고 반투명한 **'스프레이 페인트 자국'**(3D 가우시안) 수백만 개를 사용해 장면을 구성한다고 생각해 봅시다. 어떤 자국은 동그랗고, 어떤 자국은 테이블 모서리나 나뭇잎 표면을 따라 바늘처럼 얇게 늘어져 있습니다(비등방성). 이 수백만 개의 유색 '스플래트(splat)'를 겹겹이 쌓아 올리면, 어떤 각도에서도 복잡한 장면을 아주 빠르게 재현할 수 있습니다. 이는 마치 기존 그래픽스에서 삼각형을 그리는 것처럼 빠르면서도 사진 같은 부드러움과 디테일을 동시에 가집니다.

### 3. 혁신적인 지점
이 논문의 핵심 통찰은 NeRF의 비용이 많이 드는 '볼륨 레이 마칭(Volumetric Ray-marching)'을 **미분 가능한 3D 가우시안 스플래팅**과 고성능 **타일 기반 래스터라이저**(Rasterizer)로 대체한 것입니다. 장면을 2D로 투영할 수 있는 수백만 개의 타원체 집합으로 명시적으로 표현함으로써, 하드웨어 가속 기반의 정렬과 블렌딩을 가능하게 했습니다. '함수를 쿼리하는 방식(암시적)'에서 '기하학적 기본 단위를 그리는 방식(명시적)'으로의 전환을 통해, 초당 100프레임 이상의 속도로 최상급 NeRF 모델에 필적하는 화질을 구현해냈습니다.

### 4. 기술적 메커니즘

#### 4.1 파이프라인
![Pipeline Figure](figures/fig02_pipeline.png)
- 워크플로우는 SfM(Structure-from-Motion)을 통해 얻은 희소한 포인트 클라우드에서 시작하여 이를 3D 가우시안 집합으로 변환합니다. 이 가우시안들은 위치, 회전, 크기, 투명도, 색상(구면 조화 함수)에 대해 최적화되며, 실시간 피드백이 가능한 타일 기반 미분 래스터라이저를 거치게 됩니다.
- (1) 위 그림은 입력된 희소 포인트들로부터 조밀하고 최적화된 래디언스 필드로 변하는 전체 과정을 보여줍니다. (2) 장면의 빈틈을 메우는 데 결정적인 역할을 하는 '적응형 밀도 제어(Adaptive Density Control)' 단계를 주목하십시오.

#### 4.2 아키텍처 / 핵심 설계
![Architecture Figure](figures/fig04_densification.png)
- 시스템의 핵심 로직은 **적응형 가우시안 고밀도화**(Adaptive Gaussian Densification)입니다. 가우시안의 개수를 고정하지 않고, 장면이 복잡하거나 재구성이 부족한 부분에 동적으로 더 많은 '자국'을 생성합니다. 빈 공간을 채우기 위해 작은 가우시안을 '복제(Clone)'하거나, 뭉툭하고 흐린 큰 가우시안을 더 작고 날카로운 여러 개로 '분할(Split)'하여 미세한 디테일을 잡아냅니다.
- (1) 이 그림은 모델이 어떻게 '재구성 부족(Under-Reconstruction)' 구역과 '과잉 재구성(Over-Reconstruction)' 구역을 식별하는지 설명합니다. (2) '분할'과 '복제' 연산을 통해 모델은 장면의 복잡도에 맞춰 스스로 해상도를 조절합니다.

#### 4.3 핵심 방정식
- **선정 이유**: 이 방정식은 3D 가우시안의 형태(공분산 행렬)를 어떻게 매개변수화하여, 경사 하강법으로 안전하게 최적화하면서도 물리적으로 타당한 형태(양의 준정부호 행렬)를 유지할 수 있는지 설명합니다.
- **방정식**: $\Sigma = R S S^T R^T$
- 이 공식은 가우시안 타원체의 형태를 '늘어남(Scaling $S$)'과 '방향(Rotation $R$)'이라는 두 가지 독립적인 요소로 분해합니다.
- **변수 설명**:
  - $\Sigma$ = 가우시안의 형태와 크기를 나타내는 3D 공분산 행렬.
  - $R$ = 최적화된 단위 사원수(quaternion) $q$로부터 유도된 회전 행렬.
  - $S$ = 최적화된 3D 벡터 $s$로부터 유도된 스케일링 행렬.

#### 4.4 비교 분석: 기존 기술 vs 본 논문
3D 가우시안 스플래팅은 암시적 유럴 볼륨에서 명시적 포인트 기반 스플래팅으로의 패러다임 전환을 의미합니다. 가장 강력한 경쟁 모델인 Mip-NeRF360은 뛰어난 화질을 보여주지만 한 프레임을 렌더링하는 데 수 분이 걸립니다. 반면 본 논문은 실시간 렌더링이 가능하면서도 동등하거나 더 우수한 화질을 달성했습니다(Sec 7.1). MVS 기반 지형 방식에서 벗어나 비등방성 가우시안을 선택함으로써 기존 포인트 기반 렌더링의 고질적인 아티팩트(Fig 11)를 피하고, 조밀한 격자 방식의 학습 오버헤드를 줄였습니다. 주요 절충점은 수백만 개의 가우시안을 저장하기 위한 메모리 요구량으로, 복잡한 장면의 경우 수 기가바이트에 달할 수 있습니다(Sec 7.5).

#### 4.5 정성적 결과
![Qualitative Results](figures/fig05_qualitative.png)
결과물은 자전거 바퀴살이나 정원의 나뭇잎처럼 얇고 미세한 구조물에서 탁월한 재구성 능력을 보여줍니다. Instant-NGP 같은 기존 방식들이 흔히 흐릿하거나 픽셀이 깨지는 아티팩트를 만드는 것과 대조적입니다. Mip-NeRF360과 나란히 비교했을 때 선명도와 시점 종속적 반사 측면에서 육안으로 구분하기 힘들 정도로 우수합니다. 'Bicycle'과 'Garden' 장면에서 볼 수 있듯이, 금속 표면의 하이라이트와 자연물의 복잡한 텍스처를 Plenoxels보다 훨씬 잘 보존하고 있습니다(Table 1 / Fig 5). 한계점으로는 시점 종속 효과가 충분히 수렴되지 않은 매우 희소한 영역에서 간혹 '바늘 모양'의 아티팩트가 나타날 수 있다는 점이 언급되었습니다.

### 5. 영향 및 전망
이 논문은 고화질 래디언스 필드 분야의 '느린 렌더링' 시대를 사실상 종식시켰습니다. 실시간 미분 가능한 래스터라이제이션 파이프라인을 제공함으로써 VR, 디지털 트윈, 실시간 영화급 렌더링 등의 응용 분야를 열었습니다. 3D 가우시안 스플래팅은 이후 명시적 래디언스 필드 연구의 새로운 표준이 되었으며, 압축, 애니메이션, 대규모 매핑 등을 주제로 하는 수많은 후속 연구를 낳았습니다.

### 6. 더 읽어보기
- [SuGaR: Surface-Aligned Gaussian Splatting](https://arxiv.org/abs/2311.16523) - 가우시안을 장면 표면에 정렬시켜 고품질 메시(Mesh)를 추출하는 방법.
- [4D Gaussian Splatting for Real-Time Dynamic Scene Rendering](https://arxiv.org/abs/2310.08585) - 움직이는 물체가 있는 동적인 장면으로 표현을 확장.
- [GaussianPro: 3D Gaussian Splatting with Progressive Propagation](https://arxiv.org/abs/2402.14650) - 복잡한 지형에서 더 나은 품질을 위해 밀도 제어 메커니즘을 개선.
- [Compact 3D Gaussian Splatting](https://arxiv.org/abs/2311.13681) - 가우시안 표현을 압축하여 메모리 병목 현상을 해결.
- [Zip-NeRF: Anti-Aliased Grid-Based Neural Radiance Fields](https://arxiv.org/abs/2304.06706) - 비슷한 시기에 발표된 격자 기반 NeRF 방식의 정점으로 비교 대상임.
