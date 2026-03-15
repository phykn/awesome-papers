# NeRF: 視点合成のためのニューラル放射輝度場としてのシーン表現 (Representing Scenes as Neural Radiance Fields for View Synthesis)

- **著者**: Ben Mildenhall, Pratul P. Srinivasan, Matthew Tancik, Jonathan T. Barron, Ravi Ramamoorthi, Ren Ng
- **学会/日付**: ECCV 2020
- **URL**: [https://arxiv.org/abs/2003.08934](https://arxiv.org/abs/2003.08934)
- **GitHub**: [https://github.com/bmild/nerf](https://github.com/bmild/nerf)

---

### 1. 背景 (Background)
従来の視点合成（View Synthesis）方式の多くは、ボクセルグリッド（Voxel grids）、メッシュ（Meshes）、または多平面画像（Multi-plane images）といった不連続な表現方式に依存していました。これらの手法はメモリ消費が大きいという欠点がありました。例えば、ボクセルは解像度に応じて3乗でメモリ使用量が増加するため、複雑なシーンを表現する際に結果がぼやけたり、シーンの複雑さが制限されたりしました。メッシュは複雑な位相や透明度を表現するのに困難がありました。したがって、グリッドの固定されたメモリオーバーヘッドなしにシーンを連続的に表現し、複雑な幾何構造と外観を高解像度で合成できる新しいアプローチが必要でした。

### 2. 直感 (Intuition)
3次元空間が半透明の霧で満たされており、空間の各地点ごとに特定の密度と、見る角度に応じて変化する色を持っていると想像してみてください。この「霧」は固形物ではなく、空間の連続的な属性です。NeRFの核心論理は、シーンを表面の集合ではなく「放射輝度（Radiance）」と「不透明度（Opacity）」の連続的なフィールド（Field）として扱うことで、これと一致します。私たちがピクセルを見る際、この霧の中に懐中電灯（光線）を照らし、その霧が反射する光を蓄積することになりますが、これは実際の光の伝達過程をそのまま模倣したものです。

### 3. 突破口 (Breakthrough)
この論文の決定的な洞察（Aha! insight）は、ボクセルのような不連続な保存方式の代わりに、ニューラルネットワークでパラメータ化された**連続関数**を使用することです。テーブルから値を探す代わりに、3次元座標と2次元の視線方向を入力として多層パーセプトロン（MLP）に問い合わせると、該当する地点の密度と色を得ることができます。このような「座標ベース（Coordinate-based）」の表現方式のおかげで、シーンの解像度は物理的なグリッドサイズではなく、ニューラルネットワークの容量によってのみ制限されることになります。

### 4. 技術的メカニズム (Technical Mechanism)

#### 4.1 パイプライン (Pipeline)
![Pipeline Figure](figures/fig02_pipeline.png)
- (1) この図は、2Dピクセル光線から3次元サンプリングおよびボリュームレンダリングに至るエンドツーエンドの過程を示しています。(2) カメラ光線(a)に沿って地点をサンプリングすることが、ニューラル放射輝度場に問い合わせる前の最初のステップです。

#### 4.2 アーキテクチャ (Architecture)
![Architecture Figure](figures/fig07_architecture.png)
- (1) この図は、3次元位置と2次元の視線方向が別に処理されるMLP構造を描写しています。(2) 密度 $\sigma$ は位置情報のみを使用して予測されますが、これは複数の視点から見ても幾何学的な整合性を維持するためであり、色 $\mathbf{c}$ は視点に応じて変化できるように設計されています。

#### 4.3 核心公式 (Core Equation)
- **公式**: $C(\mathbf{r}) = \int_{t_n}^{t_f} T(t) \sigma(\mathbf{r}(t)) \mathbf{c}(\mathbf{r}(t), \mathbf{d}) dt$, ただし $T(t) = \exp\left(-\int_{t_n}^t \sigma(\mathbf{r}(s)) ds\right)$
- この公式は、近平面（near plane）から遠平面（far plane）まで光線に沿ったすべての点の密度と色を積分して、カメラ光線の予想色を計算します。$T(t)$ は「透過率（Transmittance）」係数で、光が他の粒子にぶつからずにその地点まで到達する確率を表します。
- **変数**:
  - $C(\mathbf{r})$ = 光線 $\mathbf{r}$ に対して予測された最終的なRGBカラー (公式2 / セクション4)。
  - $\sigma(\mathbf{x})$ = 地点 $\mathbf{x}$ でのボリューム密度であり、光線が粒子にぶつかる微分確率を意味 (公式1 / セクション3)。
  - $\mathbf{c}(\mathbf{x}, \mathbf{d})$ = 方向 $\mathbf{d}$ から見た地点 $\mathbf{x}$ の視点依存のRGBカラー (公式1 / セクション3)。
  - $T(t)$ = $t_n$ から $t$ まで光線に沿って蓄積された透過率 (公式3 / セクション4)。

#### 4.4 比較: 他の技術 vs この論文 (Evidence-Based)
NeRFは、微細で高周波な質感や複雑な鏡面反射（Specular reflection）を捉えるにおいて、SRNやNVといった以前の手法を大きく上回ります。SRNは鮮明さを維持できず、NVはボクセル解像度によって制限されるのに対し、NeRFは位置エンコーディング（Positional Encoding）と階層的サンプリング（Hierarchical Sampling）を活用して最先端の性能を達成しました (Section 6 / Table 1)。連続的なMLPベースの表現は、多平面画像でよく発生する不連続アーティファクトを除去します。ただし、NeRFは新しいシーンごとに大規模な最適化時間が必要であり、単一のGPUで通常1〜2日かかります (Section 6)。この手法の核心的な差別化ポイントは、座標ベースのニューラル表現と古典的なボリュームレンダリングの結合です。

#### 4.5 定性的結果 (Qualitative Results)
![Qualitative Results](figures/fig06_qualitative.png)
定性的な比較を通じて、NeRFがSRN、NV、LLFFなどのベースラインが見逃しやすい複雑な詳細や現実的な非ランバート（Non-Lambertian）効果をどのように再構成するかを確認できます。「Realistic Synthetic 360°」データセットの合成オブジェクトに対して、NeRFはSRNやLLFFに比べてはるかに鮮明な結果と少ないアーティファクトを示しています。SRNはしばしば表面を滑らかすぎたりぼやけさせたりして出力し、NVは目に見えるボクセル化現象が発生します。LLFFは複雑な領域で残像（Ghosting）や多視点整合性の不足を見せます。NeRFの結果は多くの場合、実際の正解（Ground Truth）画像と視覚的に区別不可能なほどです (Fig 6)。

### 5. 影響 (Impact)
NeRFは、複雑な3Dシーンを連続関数であるニューラルネットワークを使用して効率的に保存およびレンダリングできることを証明することで、コンピュータビジョンおよびグラフィックス分野を革新しました。これはニューラル放射輝度場（Neural Radiance Fields）に対する巨大な研究の流れを触発し、3D再構成、ロボティクス、仮想現実分野の発展を導きました。NeRFの成功は、高速な派生形であるInstant-NGPや大規模な応用であるBlock-NeRFといった後続研究に直接的なインスピレーションを与えました。

### 6. 後続研究 (After This Paper)
- [Mip-NeRF: A Multiscale Representation for Anti-Aliasing Neural Radiance Fields](https://arxiv.org/abs/2103.13415) - エイリアシング問題を解決し、様々なスケールでレンダリング品質を改善しました。
- [Instant Neural Graphics Primitives with a Multiresolution Hash Encoding](https://nvlabs.github.io/instant-ngp/) - ハッシュエンコーディングを通じて学習およびレンダリング速度を数日から数秒単位に画期的に短縮しました。
- [NeRF in the Wild: Neural Radiance Fields for Unconstrained Photo Collections](https://nerf-w.github.io/) - インターネット上の観光客の写真のように照明が異なり、動く物体がある環境でもNeRFが動作するように改善しました。
- [Block-NeRF: Scalable Neural Radiance Fields for Entire City Blocks](https://waymo.com/research/block-nerf/) - 都市全体の通りのような大規模な環境を表現できるようにNeRFを拡張しました。
- [RawNeRF: Preparing for Real HDR View Synthesis with Neural Radiance Fields](https://cvgl.stanford.edu/projects/rawnerf/) - カメラのRAWデータを直接学習し、ハイダイナミックレンジ（HDR）視点合成とノイズ除去を可能にしました。
