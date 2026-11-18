# GeoSentinel AI - AI/NLP Processing Engine

## Architecture Overview
The NLP engine converts cleaned, deduplicated unstructured articles into structured geopolitical event records:
$$(c, k, S_{a}, w_{k}, \text{timestamp})$$

---

## 1. 4-Domain Event Classification (TF-IDF / Linear Classifier)
- **Classes**: `CONFLICT`, `SECURITY`, `ECONOMY`, `DIPLOMACY`
- **Domain Severity Weights**:
  - `CONFLICT`: 1.00
  - `SECURITY`: 0.80
  - `ECONOMY`: 0.55
  - `DIPLOMACY`: 0.35
- **Academic Target**: Macro F1 $\ge 0.85$
- **Output**: Predicted category, confidence score ($[0.0, 1.0]$), and model version tag (`tfidf-logistic-v1`).

---

## 2. Named Entity Recognition & Country Resolution (spaCy)
- **NER Pipeline**: Extracts geopolitical entities (`GPE`), locations (`LOC`), organizations (`ORG`), and key figures (`PERSON`).
- **ISO-3166-1 Alpha-3 Normalizer**: Automatically normalizes variant spellings and aliases (e.g. "US", "U.S.A.", "United States", "White House" $\to$ `USA`; "Russian Federation", "Kremlin" $\to$ `RUS`; "Beijing", "PRC" $\to$ `CHN`).

---

## 3. Sentiment & Severity Analysis (NLTK VADER)
- **Sentiment Polarity**: Bounded in $[-1.0, +1.0]$:
  - $-1.0$: Strongly Negative
  - $0.0$: Neutral
  - $+1.0$: Strongly Positive
- **Severity Rating**: Derived from composite category baseline weight, negative polarity escalation, and tactical keyword severity indicators, strictly bounded in $[0.0, 1.0]$.

---

## 4. Executive Summarization (Extractive 3-Bullet Engine)
- **Model**: Extractive 3-Bullet Briefing Engine (`extractive-heuristics-v1`)
- **Format**: Standardized 3-bullet decision-maker briefings:
  1. `• Key development:`
  2. `• Strategic significance:`
  3. `• Geopolitical implication:`
- **Target Evaluation Metric**: Zero-hallucination factual consistency and ROUGE-L alignment.
