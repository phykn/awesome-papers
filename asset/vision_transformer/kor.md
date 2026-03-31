# An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale
- **Authors**: Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, Jakob Uszkoreit, Neil Houlsby
- **Venue/Date**: ICLR 2021
- **URL**: https://arxiv.org/abs/2010.11929
- **GitHub**: https://github.com/google-research/vision_transformer

### 1. 배경
- 이미지 특징 추출을 위한 기존의 접근법은 합성곱 신경망(CNN)에 크게 의존하여, 국소적인 수용 영역으로 인해 전역적인 관계를 포착하는 데 한계가 있었습니다.
- 트랜스포머가 자연어 처리를 완전히 바꾼 반면, 이미지를 픽셀 단위로 트랜스포머에 직접 적용하는 것은 계산적으로 효율적이지 않았습니다. 본 논문은 이미지를 겹치지 않는 여러 개의 '패치(patch)'로 분할하여 접근함으로써 순수 트랜스포머 모델도 CNN의 최고 성능에 맞먹을 수 있음을 증명했습니다.

### 2. 직관적인 이해
- 그림책을 본다고 상상해 보세요. 조그마한 돋보기를 통해 점 단위로 그림을 분석하는 것(CNN과 유사)이 아니라, 전체 이미지를 일정한 격자 모양의 플래시 카드로 잘라냅니다.
- **Vision Transformer**(ViT)는 각각의 16x16 패치 플래시 카드를 문장 내 하나의 단어처럼 취급하여, 모델이 이미지 전체에서 발생하는 모든 세부 사항들을 즉각적으로 연관 지을 수 있게 해줍니다.

### 3. 핵심 돌파구
- 핵심적인 통찰은 합성곱 연산을 완전히 배제한 것입니다. 중복되지 않는 패치들을 1차원 벡터로 평탄화하고 위치 정보와 함께 표준 자연어 트랜스포머에 입력함으로써, 신경망은 인간이 설정한 시각적 편향 없이도 전역적 맥락을 학습하게 됩니다.

### 4. 기술적 동작 원리

#### 4.1 파이프라인
![Pipeline Figure](figures/fig01_pipeline.png)
- 입력 이미지는 고정된 크기의 패치로 쪼개지며, 선형 임베딩 및 위치 정보가 더해진 뒤 학습을 위한 전용 분류 토큰과 함께 트랜스포머 인코더로 전달됩니다.
- 보여주는 것: 패치 토큰을 활용한 이미지의 종단간(End-to-End) 처리 과정.
- 핵심 변수: 최상단 출력 계층의 `[class]` 토큰이 최종적인 예측을 전적으로 결정합니다.

#### 4.2 아키텍처 및 핵심 설계
![Architecture Figure](figures/fig01_pipeline.png)
- 내부 구조는 기존 자연어 트랜스포머 인코더의 형태를 엄격하게 따르며 다중 헤드 자기 주의(Multi-Head Self Attention) 연산과 다층 퍼셉트론(MLP) 블록을 교차로 쌓아 올렸습니다.
- 보여주는 것: 트랜스포머 계층별 정보의 흐름과 정규화.
- 핵심 설계: 이동 등변성이나 국소성과 같은 시각적 편향을 배제하고 자기 주의 메커니즘에만 전적으로 의존하여, 대용량 데이터로부터 이미지의 지역적 구조를 스스로 학습하도록 강제합니다.

#### 4.3 핵심 수식
- 자기 주의 메커니즘을 통해 모든 인접 패치들 사이의 관계를 찾아냅니다.

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

- $Q$: 관련된 맥락 정보 파악을 위해 쿼리를 던지는 패치들의 매트릭스 (Sec 3.1).
- $K$: 쿼리에 응답하기 위해 특징을 제공하는 키 매트릭스.
- $V$: 최종적으로 취합할 시각적 정보를 담고 있는 값 매트릭스.
- $d_k$: 키의 차원 크기로, 내적한 배율을 축소시켜 그래디언트를 안정화시킵니다.

#### 4.4 비교: 기존 모델 vs 본 논문
- 저자들은 충분히 방대한 데이터셋에서 사전 학습될 경우 순수 트랜스포머가 정교하게 설계된 최신 CNN 아키텍처를 뛰어넘는다고 주장합니다. ResNet과 같은 기존 CNN은 초기 계층에서 전역적인 수용 영역을 확보하지 못해 전체적인 이해 능력이 제한적입니다. 반면 ViT는 시각적 연산자를 일절 사용하지 않고 자기 주의 연산만을 활용하여 차별화됩니다. 이 메커니즘은 가장 낮은 계층부터 장거리 의존성을 광범위하게 학습할 수 있도록 해줍니다 (Fig 11 참조). 단, CNN 구조에 내재된 위치 보조적 편향이 없기 때문에 밑바닥부터 관계를 학습해야 하여(JFT-300M과 같은) 엄청난 규모의 사전 학습 데이터가 필요하다는 것이 트레이드오프(Trade-off)입니다.

#### 4.5 정성적 결과
![Qualitative Results](figures/fig06_qualitative.png)
- 최종 분류 토큰에서 입력 이미지 공간 방향으로 주의(Attention) 맵을 투영해보면, ViT가 이미지 내에서 의미 있는 영역을 아주 자연스럽게 발견함을 알 수 있습니다.
- 모델은 어떤 명시적이고 공간적인 구조 제약이 없었음에도 불구하고 바탕이나 노이즈를 억제하고 주요 피사체를 똑바로 지시하며 추론합니다.

### 5. 영향 및 파급력
- ViT는 최고 수준의 이미지 인식을 위해 합성곱 블록이 필수적이라는 기존의 고정관념을 무너뜨리며 컴퓨터 비전의 패러다임을 바꿨습니다. 궁극적으로 자연어처리와 컴퓨터 비전 영역의 구조를 통합하였고, 곧바로 멀티모달 및 시각 파운데이션 모델의 새로운 시대를 열었습니다.

### 6. 추가 읽기 자료
[1] [Attention Is All You Need (2017)](https://arxiv.org/abs/1706.03762)<br>
원본 트랜스포머 아키텍처를 도입하여 기초를 닦은 기반 논문입니다.<br>
[2] [Training data-efficient image transformers & distillation through attention (2020)](https://arxiv.org/abs/2012.12877)<br>
방대한 규모의 사전 학습을 요구하지 않으면서 적은 데이터셋에서도 ViT를 안전하고 효율적으로 훈련할 수 있는 전략을 제시합니다.<br>
[3] [Swin Transformer: Hierarchical Vision Transformer using Shifted Windows (2021)](https://arxiv.org/abs/2103.14030)<br>
부분 이동 윈도우(Shifted window) 내에서 자기 주의 연산을 계산해 계층적 표현과 뛰어난 효율성을 제공하도록 ViT 구조를 확장했습니다.<br>
