# NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis

- **저자**: Ben Mildenhall, Pratul P. Srinivasan, Matthew Tancik, Jonathan T. Barron, Ravi Ramamoorthi, Ren Ng
- **학회/날짜**: ECCV 2020
- **URL**: [https://arxiv.org/abs/2003.08934](https://arxiv.org/abs/2003.08934)
- **GitHub**: [https://github.com/bmild/nerf](https://github.com/bmild/nerf)

---

### 1. 배경
기존의 시점 합성(View Synthesis) 방식은 대부분 복셀 그리드(Voxel grids), 메쉬(Meshes), 또는 다중 평면 이미지(Multi-plane images)와 같은 불연속적인 표현 방식에 의존했습니다. 이러한 방법들은 메모리 소비가 크다는 단점이 있었습니다. 예를 들어 복셀은 해상도에 따라 세제곱으로 메모리 사용량이 증가하여, 복잡한 장면을 표현할 때 결과물이 흐릿해지거나 장면의 복잡도가 제한되었습니다. 메쉬는 복잡한 위상이나 투명도를 표현하는 데 어려움이 있었습니다. 따라서 그리드의 고정된 메모리 오버헤드 없이 장면을 연속적으로 표현하여, 복잡한 기하 구조와 외형을 고해상도로 합성할 수 있는 새로운 접근 방식이 필요했습니다.

### 2. 직관
3차원 공간이 반투명한 안개로 가득 차 있고, 공간의 각 지점마다 특정 밀도와 보는 각도에 따라 변하는 색상을 가지고 있다고 상상해 보세요. 이 "안개"는 단단한 물체가 아니라 공간의 연속적인 속성입니다. NeRF의 핵심 논리는 장면을 표면의 집합이 아니라 "복사휘도(Radiance)"와 "불투명도(Opacity)"의 연속적인 필드(Field)로 취급함으로써 이와 일치합니다. 우리가 픽셀을 볼 때, 이 안개 속으로 손전등(광선)을 비추고 그 안개가 반사하는 빛을 축적하는 셈인데, 이는 실제 빛의 전달 과정을 그대로 모사한 것입니다.

### 3. 돌파구
이 논문의 결정적인 통찰(Aha! insight)은 복셀과 같은 불연속적인 저장 방식 대신, 신경망으로 매개변수화된 **연속 함수**를 사용하는 것입니다. 표에서 값을 찾는 대신, 3차원 좌표와 2차원 시각 방향을 입력으로 하여 다층 퍼셉트론(MLP)에 질의하면 해당 지점의 밀도와 색상을 얻을 수 있습니다. 이러한 "좌표 기반(Coordinate-based)" 표현 방식 덕분에 장면의 해상도는 물리적인 그리드 크기가 아니라 신경망의 용량에 의해서만 제한되게 됩니다.

### 4. 기술적 메커니즘

#### 4.1 파이프라인
![Pipeline Figure](figures/fig02_pipeline.png)
- (1) 이 그림은 2D 픽셀 광선에서 3차원 샘플링 및 볼륨 렌더링에 이르는 엔드투엔드 과정을 보여줍니다. (2) 카메라 광선(a)을 따라 지점들을 샘플링하는 것이 신경 복사 필드에 질의하기 전의 첫 번째 단계입니다.

#### 4.2 아키텍처 (Architecture)
![Architecture Figure](figures/fig07_architecture.png)
- (1) 이 그림은 3차원 위치와 2차원 시각 방향이 별도로 처리되는 MLP 구조를 묘사합니다. (2) 밀도 ($\sigma$)는 위치 정보만을 사용하여 예측되는데, 이는 여러 시점에서 보더라도 기하학적 일관성을 유지하기 위함이며, 색상 ($\mathbf{c}$)는 시점에 따라 변할 수 있도록 설계되었습니다.

#### 4.3 핵심 공식
- **공식**: $C(\mathbf{r}) = \int_{t\_n}^{t\_f} T(t) \sigma(\mathbf{r}(t)) \mathbf{c}(\mathbf{r}(t), \mathbf{d}) dt$, 단 $T(t) = \exp\left(-\int_{t\_n}^t \sigma(\mathbf{r}(s)) ds\right)$
- 이 공식은 근평면(near plane)부터 원평면(far plane)까지 광선을 따라 있는 모든 점의 밀도와 색상을 적분하여 카메라 광선의 예상 색상을 계산합니다. $T(t)$ 는 "투과율(Transmittance)" 계수로, 빛이 다른 입자에 부딪히지 않고 해당 지점까지 도달할 확률을 나타냅니다.
- **변수**:
  - $C(\mathbf{r})$: 광선 $\mathbf{r}$에 대해 예측된 최종 RGB 색상 (공식 2 / 섹션 4).
  - $\sigma(\mathbf{x})$: 지점 $\mathbf{x}$에서의 볼륨 밀도이며, 광선이 입자에 부딪힐 미분 확률을 의미 (공식 1 / 섹션 3).
  - $\mathbf{c}(\mathbf{x}, \mathbf{d})$: 방향 $\mathbf{d}$에서 바라본 지점 $\mathbf{x}$의 시점 의존적 RGB 색상 (공식 1 / 섹션 3).
  - $T(t)$: $t\_n$부터 $t$까지 광선을 따라 축적된 투과율 (공식 3 / 섹션 4).


#### 4.4 비교: 다른 기술 vs 이 논문
NeRF는 미세하고 고주파적인 질감과 복잡한 거울 반사(Specular reflection)를 포착하는 데 있어 SRN이나 NV와 같은 이전 방법들을 크게 앞섭니다. SRN은 선명도를 유지하지 못하고 NV는 복셀 해상도에 의해 제한되는 반면, NeRF는 위치 인코딩(Positional Encoding)과 계층적 샘플링(Hierarchical Sampling)을 활용하여 최첨단 성능을 달성했습니다 (Section 6 / Table 1). 연속적인 MLP 기반 표현은 다중 평면 이미지에서 흔히 발생하는 불연속 아티팩트를 제거합니다. 다만, NeRF는 새로운 장면마다 대규모 최적화 시간이 필요하며, 단일 GPU에서 보통 1~2일이 소요됩니다 (Section 6). 이 방법의 핵심 차별점은 좌표 기반 신경 표현과 고전적인 볼륨 렌더링의 결합입니다.

#### 4.5 정성적 결과
![Qualitative Results](figures/fig06_qualitative.png)
정성적 비교를 통해 NeRF가 SRN, NV, LLFF와 같은 베이스라인들이 놓치기 쉬운 복잡한 세부 사항과 현실적인 비람버트(Non-Lambertian) 효과를 어떻게 재구성하는지 확인할 수 있습니다. "Realistic Synthetic 360°" 데이터셋의 합성 객체들에 대해 NeRF는 SRN이나 LLFF에 비해 훨씬 선명한 결과와 적은 아티팩트를 보여줍니다. SRN은 종종 표면을 너무 매끄럽거나 흐릿하게 출력하고, NV는 눈에 보이는 복셀화 현상이 발생합니다. LLFF는 복잡한 영역에서 잔상(Ghosting)이나 다중 시점 일관성 부족을 보입니다. NeRF의 결과는 많은 경우 실제 정답(Ground Truth) 이미지와 시각적으로 구분이 불가능할 정도입니다 (Fig 6).

### 5. 영향
NeRF는 복잡한 3D 장면을 연속 함수인 신경망을 사용하여 효율적으로 저장하고 렌더링할 수 있음을 증명함으로써 컴퓨터 비전 및 그래픽스 분야를 혁신했습니다. 이는 신경 복사 필드(Neural Radiance Fields)에 대한 거대한 연구 흐름을 촉발했으며, 3D 재구성, 로보틱스, 가상 현실 분야의 발전을 이끌었습니다. NeRF의 성공은 고속 변체인 Instant-NGP나 대규모 응용인 Block-NeRF와 같은 후속 연구들에 직접적인 영감을 주었습니다.

### 6. 후속 연구
[1] [Mip-NeRF: A Multiscale Representation for Anti-Aliasing Neural Radiance Fields (2021)](https://arxiv.org/abs/2103.13415)<br>
앨리어싱 문제를 해결하고 다양한 스케일에서 렌더링 품질을 개선했습니다.
[2] [Instant Neural Graphics Primitives with a Multiresolution Hash Encoding](https://nvlabs.github.io/instant-ngp/)<br>
해시 인코딩을 통해 학습 및 렌더링 속도를 며칠에서 몇 초 단위로 획기적으로 단축했습니다.
[3] [NeRF in the Wild: Neural Radiance Fields for Unconstrained Photo Collections](https://nerf-w.github.io/)<br>
인터넷 상의 관광객 사진처럼 조명이 다르고 움직이는 물체가 있는 환경에서도 NeRF가 작동하도록 개선했습니다.
[4] [Block-NeRF: Scalable Neural Radiance Fields for Entire City Blocks](https://waymo.com/research/block-nerf/)<br>
도시 전체 거리와 같은 대규모 환경을 표현할 수 있도록 NeRF를 확장했습니다.
[5] [RawNeRF: Preparing for Real HDR View Synthesis with Neural Radiance Fields](https://bmild.github.io/rawnerf/)<br>
카메라의 RAW 데이터를 직접 학습하여 고역동성 범위(HDR) 시점 합성과 노이즈 제거를 가능하게 했습니다.
