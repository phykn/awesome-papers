# Zip-NeRF: Anti-Aliased Grid-Based Neural Radiance Fields
- **Authors**: Jonathan T. Barron, Ben Mildenhall, Dor Verbin, Pratul P. Srinivasan, Peter Hedman
- **Venue/Date**: ICCV 2023
- **URL**: https://arxiv.org/abs/2304.06706
- **GitHub**: https://github.com/google-research/zip-nerf

### 1. 背景
標準的な神経放射場 (NeRF) には、学習/レンダリングの遅さと、エイリアシング (ジャギー) という2つの大きな問題がありました。Mip-NeRF は円錐台を使用してエイリアシングを解決しましたが、低速でした。一方、Instant NGP は高速なグリッドベースの表現を導入しましたが、離散的な点サンプリングによりエイリアシングが再発しました。Zip-NeRF は、グリッドの**速度**と円錐台の**アンチエイリアス**性能を両立させることを目指しています。

### 2. 直感
非常に細い筆でグリッドを塗ろうとしている状況を想像してください (グリッドベースの NeRF)。筆をわずかに動かすだけで、色が急激に変わってしまいます (エイリアシング)。Zip-NeRF は、各ピクセルに対して複数の小さな筆を同時に使い、グリッドに適用する前にそれらの色を平均化するようなものです。これにより、どのように動かしてもスムーズな変換が保証されます。

### 3. 核心的な突破口
核心的な突破口は、Instant NGP のグリッドピラミッドを mip-NeRF 360 のフレームワークに統合する**マルチサンプリング**戦略です。六角形のマルチサンプリングパターンと事前フィルタリングされた損失 (prefiltered loss) を使用することで、ハッシュベースのエンコーディングの速度を犠牲にすることなく、グリッドボクセルのスケールを「推論」できるようになりました。

### 4. 技術的メカニズム

#### 4.1 Pipeline
![Pipeline Figure](figures/fig02_pipeline.png)
- パイプラインは、多解像度ハッシュグリッドとマルチサンプリング戦略を統合します。単一の点ではなく、円錐台の体積を表現するために、間隔ごとに6つの点を六角形パターンでサンプリングします。
- コアモジュール: 多解像度ハッシュグリッドと各フラスタム6点六角形マルチサンプリングの組み合わせ。

#### 4.2 Architecture / Core Design
![Architecture Figure](figures/fig03_architecture.png)
- アーキテクチャは、グリッド特徴がサンプル間で平均化されるマルチサンプリング特徴化を使用します。これにより、MLP はその深度のグリッド解像度と一致する「スケール認識」入力を得ることができます。
- 設計根拠: スケール認識入力特征化により、高周波ノイズが MLP に漏れるのを防止します (Fig 3)。

#### 4.3 Core Equation
- スケール認識特彵 $f$ は、複数サンプルの三線形補間されたハッシュグリッド特彵の平均として計算されます:
- $$f(\mathbf{x}, \sigma) = \frac{1}{J} \sum_{j=1}^{J} \text{tri}(\text{hash}(\mathbf{x}_j))$$
- Variables:
- $\mathbf{x}_j$: 円錐台内の $j$ 番目のマルチサンプリング座標 (Fig 3)。
- $\sigma$: サンプルの広がりを決定するスケールパラメータ。
- $\text{tri}$: ハッシュグリッド特徴に対する三線形補間 (Eq 2)。
- $J$: サンプル数 (本論文では 6 に固定)。

#### 4.4 Comparison: Others vs This Paper
Zip-NeRF は、mip-NeRF 360 と Instant NGP の両方を大幅に上回る性能を発揮します。mip-NeRF 360 は高品質なアンチエイリアスを提供しますが、大規模な学習には非常に低速です。Instant NGP は高速ですが、ズームイン/アウト時に深刻なエイリアシングアーティファクト (ジャギー) が発生します (Sec 4.1)。Zip-NeRF は、mip-NeRF 360 より 24 倍速く学習しながら、エラー率を 8% から 77% 低減することに成功しました (Fig 1)。主なトレードオフはマルチサンプリング特徴によるメモリ使用量のわずかな増加ですが、速度と品質の向上はそれを補って余りあるものです。

#### 4.5 Qualitative Results
![Qualitative Results](figures/fig01_teaser.png)
- 定性的な結果から、Zip-NeRF は葉や手すりのような、グリッドベースのモデルでは通常失われたり歪んだりする細い構造の復元に優れていることがわかります。正解画像 (Ground Truth) との比較 (Fig 1) では、Zip-NeRF のレンダリングは実写とほとんど見分けがつかないのに対し、従来の高速な手法では顕著なちらつきやノイズが見られます。

### 5. 影響
Zip-NeRF は、効率的で高品質な視点合成の新たな基準を打ち立てました。これは「研究レベル」の品質と「商用レベル」の速度の間のギャップを埋め、VR や高精細なデジタルツインなどの実用的なアプリケーションへの放射場の適用をより現実的なものにします。

### 6. さらなる学習

[1] [Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields (2021)](https://arxiv.org/abs/2111.12077)<br>
非線形シーン収縮とアンチエイリアス円錐台を導入し、無境界シーンを扱った先行研究。<br>
[2] [Instant Neural Graphics Primitives with a Multiresolution Hash Encoding (2022)](https://arxiv.org/abs/2201.05989)<br>
Zip-NeRF がアンチエイリアス向けに最適化する高速ハッシュグリッドベースの特彵化を導入した研究。<br>
[3] [3D Gaussian Splatting for Real-Time Radiance Field Rendering (2023)](https://arxiv.org/abs/2308.04079)<br>
ボリューメトリックフィールドの代わりに明示的な点ベースのプリミティブを使用する競合最新手法。<br>
[4] [MERF: Memory-Efficient Radiance Fields for Real-Time View Synthesis (2023)](https://arxiv.org/abs/2302.12249)<br>
リアルタイムブラウザベースの放射場レンダリングに特化したハイブリッド表現方式。<br>
[5] [NeRF: Representing Scenes as Neural Radiance Fields (2020)](https://arxiv.org/abs/2003.08934)<br>
神経放射場革命を開始した基礎論文。<br>

