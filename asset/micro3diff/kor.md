# Multi-plane denoising diffusion-based dimensionality expansion for 2D-to-3D reconstruction of microstructures with harmonized sampling

- **저자**: Kang-Hyun Lee, Gun Jin Yun
- **학회/날짜**: npj Computational Materials (2024)
- **URL**: [https://doi.org/10.1038/s41524-024-01280-z](https://doi.org/10.1038/s41524-024-01280-z)
- **GitHub**: Not specified in the paper.

---

### 1. 배경
3차원 미세구조를 특성화하는 것은 재료의 특성을 이해하는 데 필수적이지만, X-ray CT나 연속 절단법(serial sectioning) 등을 통해 3D 데이터셋을 획득하는 것은 비용과 시간이 매우 많이 듭니다. 반면, 2D 미세조직 사진(micrographs)은 풍부하고 획득하기 쉽습니다. 기존의 2D-to-3D 재구성 방법들은 방대한 3D 학습 데이터에 의존하거나, 3차원 공간에서의 공간적 연결성과 물리적 사실성을 유지하는 데 어려움이 있었습니다. 따라서 고가의 3D 데이터 없이도 2D 지식을 3D로 확장할 수 있는 새로운 프레임워크가 절실히 필요했습니다.

### 2. 직관
핵심 직관은 "유효한 3D 구조라면 어떤 직교 방향(XY, YZ, ZX 평면)에서 잘라도 사실적인 2D 이미지처럼 보여야 한다"는 것입니다. 조각가가 3D 작품을 만드는 과정을 상상해 보세요. 정면, 측면, 위에서 끊임없이 모양을 확인하고 다듬음으로써 전체적으로 일관된 형태를 완성합니다. Micro3Diff는 이 원리를 적용하여, 사전 학습된 2D 확산 모델(Diffusion Model)을 사용해 세 방향의 모든 단면을 동시에 "노이즈 제거(denoising)"하거나 "정제"함으로써, 이들이 하나의 연결된 3D 볼륨으로 조화롭게 합쳐지도록 강제합니다.

### 3. 돌파구
이 논문의 결정적인 통찰(Aha! insight)은 **차원 확장(dimensionality expansion)을 학습 단계가 아닌 추론(sampling) 단계에서 수행**한다는 것입니다. 이는 기존에 이미 구축된 고품질의 2D 확산 생성 모델(DGM)을 그대로 활용할 수 있음을 의미하며, 생성 과정에서만 3D 일관성을 부여하면 됩니다. 결과적으로 별도의 3D 학습 데이터가 전혀 필요하지 않아, 재료 과학자들이 매우 유연하고 효율적으로 이 프레임워크를 사용할 수 있게 되었습니다.

### 4. 기술적 메커니즘

#### 4.1 파이프라인
![Pipeline Figure](figures/fig13_pipeline.png)
- (1) 이 그림은 노이즈가 섞인 3D 복셀이 세 개의 직교 평면(XY, YZ, ZX)으로 분할되는 "다중 평면 노이즈 제거" 과정을 보여줍니다. (2) 각 단면은 2D 확산 모델에 의해 처리되며, 업데이트된 결과들이 다시 3D 볼륨으로 통합되어 공간적 연결성을 유지합니다.

#### 4.2 아키텍처 (Architecture)
![Algorithm Figure](figures/fig16_algorithm.png)
- (1) 이 도식은 차원 간 노이즈 레벨을 관리하는 "조화로운 샘플링(Harmonized Sampling)" 알고리즘을 나타냅니다. (2) 이는 2D 잠재 공간에서 3D 구조로 이동할 때 발생할 수 있는 매핑 오류를 해결하여, 역 확산 과정이 안정적인 궤적을 유지하도록 보장합니다.

#### 4.3 핵심 공식
- **공식**:

$$\hat{x}_{t-1, i} = \text{MultiPlaneDenoise}(x_{t, i}, \epsilon_\theta, \text{planes} \in \{XY, YZ, ZX\})$$

- 이 과정은 3D 볼륨 $x$를 반복적으로 정제하며, 각 평면에서의 노이즈 제거 추정치가 최종 복셀 값에 기여하도록 합니다. 이는 일반적으로 확산 역 과정에서 가중 평균이나 특정 샘플링 단계로 구현됩니다.
- **변수**:
  - $x\_t$ = 시간 단계 $t$에서의 노이즈가 섞인 3D 볼륨 (섹션 4.1).
  - $\epsilon\_\theta$ = 사전 학습된 2D 노이즈 제거 신경망(U-Net) (섹션 4.2).
  - $t$ = 완전한 노이즈에서 데이터까지 이르는 확산 시간 단계 (섹션 4.1).

#### 4.4 비교: 다른 기술 vs 이 논문
Micro3Diff는 일반적인 슬라이스별 생성 방식에 비해 우수한 3D 연결성과 형태학적 정확도를 보여줍니다. 기존 2D 방식들은 평면 외(out-of-plane) 일관성이 부족한 반면, Micro3Diff는 모든 방향에서 2점 상관 함수 ($S\_2\$) 와 선형 경로 함수 ($L\_2\$) 가 통계적으로 동일함을 입증했습니다 (Section 3 / Fig 4). 조화로운 샘플링 과정은 단순한 다중 평면 접근법에 비해 다결정 입계와 같은 복잡한 특징을 포착하는 데 있어 오류율을 대폭 낮춥니다 (Fig 5). 단, 세 평면에 대한 노이즈 제거 루프로 인해 3D 볼륨 생성당 계산 시간이 증가한다는 점이 트레이드오프(trade-off)로 언급됩니다 (Section 3.1).

#### 4.5 정성적 결과
![Qualitative Results](figures/fig02_qualitative.png)
정성적 결과는 구형 개재물, 다결정 입자(case II), 그리고 NMC 양극재와 같은 복잡한 다공성 구조를 포함한 다양한 미세구조가 성공적으로 재구성되었음을 보여줍니다. "case II"(다결정)의 경우, 생성된 3D 샘플은 원래 2D 학습 데이터의 시각적 특성과 일치하는 현실적인 입자 연결성과 3중점(triple-junction) 기하 구조를 보여줍니다 (Fig 7). 탄산염 데이터셋과 같은 다공성 매체의 경우, Micro3Diff는 배터리 성능 분석에 중요한 복잡한 네트워크 형태와 굴곡도(tortuosity)를 잘 포착합니다 (Fig 11).

### 5. 영향
Micro3Diff는 재료 정보학(Materials Informatics) 분야에 강력한 도구를 제공하여, 연구자들이 손쉽게 구할 수 있는 2D 데이터로 고충실도 3D 미세구조를 생성할 수 있게 합니다. 이는 대규모 시뮬레이션 및 통합 계산 재료 공학(ICME)의 진입 장벽을 낮추며, 쉬운 2D 데이터 획득과 필수적인 3D 특성 분석 사이의 간극을 효과적으로 메워줍니다.

### 6. 후속 연구
- [MicroLad: Latent Diffusion-Based 2D-to-3D Microstructure Reconstruction with Inverse Design](https://github.com/KangHyunL/microlad) - 잠재 공간 확산과 점수 증류(SDS)를 도입하여 물성 유도 역설계를 가능하게 한 2025년 후속 연구입니다.
