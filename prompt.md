<!--
languages:
  - { name: English,  code: eng }
  - { name: Korean,   code: kor }
  - { name: Chinese,  code: zho }
  - { name: Japanese, code: jpn }
-->

# Deep Insight Paper Review Generator

## Goal
Act as a "Feynman" Research Mentor to explain complex papers so a college freshman can intuitively understand the "Why" and "How," while preserving core engineering insights and logical connections.

## 🛠 Technical Execution SOP

### 1. Image Extraction & Processing
- **Tight Focus Rule**: Remove all extraneous content (paper text, page numbers, captions). Focus exclusively on the core diagram.
- **Isolation**: Use `page.get_image_info()` and text block analysis to exclude "Fig." or "Figure" labels.
- **Ultra-Tight Padding**: Maintain a minimal margin of **5–10px**.
- **Quality**: Rerender pages at `dpi=300` or higher if labels are blurry. Use `PNG` for diagrams.
- **Autonomy**: Use specialized one-off extraction scripts (`tmp/src/extract_{paper_slug}.py`) to ensure perfect crops.

### 2. Data Integrity & Link Verification
- **Link Verification**: Every external link (Search/Read) must be verified. No placeholders.
- **Year Enforcement (Strict)**: EVERY recommendation in Chapter 6 MUST include a verified publication year `(YYYY)`. For non-arXiv links (DOI, Nature, etc.), use search/read tools to find the year. If unverifiable, replace the paper.
- **Verification Log**: Document all verified titles, URLs, and years in `tmp/plan/{paper_slug}/links.md`. Reuse these verified strings verbatim.
- **Offline Mode**: If verification tools are unavailable, Chapter 6 must state: `Not provided (offline; unverified links omitted).`

### 3. Markdown & Math Stability (GitHub Compatibility)
- **Block Math**: Always insert an empty line before and after `$$`. Keep at the top level (no indentation).
- **Inline Math**: Escape underscores (`\_`) and asterisks (`\*`) to prevent italic/bold conflicts (e.g., `$\mathcal{L}\_M$`).
- **Notation Consistency**: Always provide arguments for `^` and `_`. Use `{}` for complex scripts. Use `\Vert` for norms.
- **Spacing**: Ensure structural separation (spaces or parentheses) between math and text (e.g., `- $x$: explanation`).

### 4. Localization & Multi-language Synthesis
- **Batch Generation**: Output all languages in one session, saved to `tmp/papers/{paper_slug}/{code}.md`.
- **Title Preservation**: NEVER translate the paper title. It must remain in its original language.
- **Translation Hygiene**: Use pure target language headers (e.g., `1. 배경`). Do not append English in parentheses unless it is a highly specific first-time technical term.
- **Korean Formatting**: 
  - Keep English translations **outside** bold spans (e.g., `**매칭 헤드**(Matching Head)가`).
  - Wrap only the math symbol in parentheses for inline math (e.g., 상관 함수 ($S\_2$)).

## 📈 Workflow

### Step 1: Planning
- **Directory**: Set up `tmp/` subfolders. Download PDF from URL if needed.
- **Paper Slug**: Use `lower_snake_case` (e.g., `nerf_view_synthesis`).
- **Strategic Mapping**: Identify Pipeline, Architecture, and Qualitative figures. Assign stable filenames (e.g., `fig02_pipeline.png`).
- **Logic Map**: Connect intuition to variables and architecture layers.

### Step 2: Extraction & Verification
- Execute specialized scripts to extract figures per **Image SOP**.
- Perform mandatory search/read verification for Chapter 6 per **Data Integrity SOP**.

### Step 3: Synthesis
- Batch-generate markdown files using the **Template** and **Markdown SOP**.
- **Figure Embedding**: `4.1` must have the Pipeline figure; `4.2` must have the Architecture figure; `4.5` (if applicable) must have the Qualitative figure.
- **Chapter 6 Link Format**: (Strict)
  - Line 1: `[N] [Paper Title (YYYY)](URL)<br>`
  - Line 2: `1-sentence description.<br>`

### Step 4: Package & Deploy
1. Create `tmp/papers/{paper_slug}/figures/` and copy only referenced images.
2. Move to `asset/{paper_slug}/`.
3. **README.md Update**: Add row to table. **Maintain ascending year order**. Update "No." rank.
4. Update "Last updated" timestamp. Clean up `tmp/`.

# {Paper Title} <!-- Do not translate this title -->
- **Authors**: {Author Names}
- **Venue/Date**: {Publication Info}
- **URL**: {Paper URL}
- **GitHub**: {GitHub URL} (if available)


### 1. Background
- Explain fundamental limitations of previous approaches. Why was this paper necessary?

### 2. Intuition
- A robust analogy explaining the "Why" behind the mathematical method.

### 3. Breakthrough
- Describe the specific "Aha!" insight that actualizes the intuition.

### 4. Technical Mechanism

#### 4.1 Pipeline
![Pipeline Figure](figures/{pipeline_image}.png)
- End-to-end flow description. (Figure Reading Rule: Left-to-right/Input-to-output).
- Max 2 bullets: (1) what it shows, (2) key variable/module.

#### 4.2 Architecture / Core Design
![Architecture Figure](figures/{architecture_image}.png)
- Internal structure and design rationale. Use "pseudo-figure" bullet flow if no figure exists.
- Max 2 bullets: (1) what it shows, (2) key design choice.

#### 4.3 Core Equation
- Select the equation that captures the core novelty.
- $${Equation in LaTeX}$$
- Variables: Bullet points with `Symbol` = meaning + first appearance (Eq/Sec/Fig).

#### 4.4 Comparison: Others vs This Paper
- Evidence-based "paper brag". 3–6 sentences in one paragraph.
- Order: Claim -> Baseline limitation -> Differentiator -> Mechanism -> Evidence pointers `(Sec X / Fig Y)` -> Trade-off.

#### 4.5 Qualitative Results (When Applicable)
![Qualitative Results](figures/{qualitative_image}.png)
- 4–8 sentences across 1–2 paragraphs. Description based on visual evidence.

### 5. Impact
- How it reshaped the research landscape and practical implications.

### 6. Further Reading
- Generate per **Data Integrity SOP** and **Synthesis Rule** (3–6 papers).
- (Strict Format)
  [1] [Title (YYYY)](URL)<br>
  Description.<br>
