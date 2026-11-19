"""
GeoSentinel AI - Inter-Annotator Agreement Evaluation
Computes Cohen's Kappa, Observed Agreement, and Discrepancy Matrix
for dual-annotated geopolitical OSINT research corpora.

Adheres strictly to academic integrity: Never fabricates human annotations.
If human annotations are pending or incomplete, cleanly reports completion
state and marks empirical validation as PENDING.
"""
import os
import sys
import json
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

CATEGORIES = ["CONFLICT", "SECURITY", "ECONOMY", "DIPLOMACY"]

def compute_cohens_kappa(labels_1: List[str], labels_2: List[str]) -> Dict[str, Any]:
    """
    Computes Cohen's Kappa (kappa) between two independent annotators:
    kappa = (P_o - P_e) / (1 - P_e)
    """
    assert len(labels_1) == len(labels_2), "Label lists must be of equal length."
    n = len(labels_1)
    if n == 0:
        return {"status": "EMPTY", "kappa": None, "observed_agreement": None}

    cat_to_idx = {cat: i for i, cat in enumerate(CATEGORIES)}
    k = len(CATEGORIES)
    conf_matrix = np.zeros((k, k), dtype=int)

    for l1, l2 in zip(labels_1, labels_2):
        if l1 in cat_to_idx and l2 in cat_to_idx:
            conf_matrix[cat_to_idx[l1], cat_to_idx[l2]] += 1

    total_valid = int(np.sum(conf_matrix))
    if total_valid == 0:
        return {"status": "NO_VALID_PAIRS", "kappa": None}

    # Observed agreement (Po)
    po = float(np.trace(conf_matrix) / total_valid)

    # Chance agreement (Pe)
    row_sums = np.sum(conf_matrix, axis=1) / total_valid
    col_sums = np.sum(conf_matrix, axis=0) / total_valid
    pe = float(np.sum(row_sums * col_sums))

    # Cohen's Kappa
    if pe >= 1.0:
        kappa = 1.0
    else:
        kappa = float((po - pe) / (1.0 - pe))

    return {
        "status": "COMPLETED",
        "total_pairs": total_valid,
        "observed_agreement": round(po, 4),
        "chance_agreement": round(pe, 4),
        "cohens_kappa": round(kappa, 4),
        "target_met": kappa >= 0.80,
        "confusion_matrix": conf_matrix.tolist(),
        "categories": CATEGORIES,
    }

def evaluate_corpus_file(corpus_path: str, output_report: Optional[str] = None) -> Dict[str, Any]:
    if not os.path.exists(corpus_path):
        result = {
            "status": "PENDING",
            "message": f"Corpus file not found at {corpus_path}. Empirical multi-annotator review pending.",
            "total_articles": 0,
            "dual_annotated_count": 0,
            "cohens_kappa": None,
        }
        if output_report:
            _write_pending_report(output_report, result)
        return result

    with open(corpus_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    total = len(articles)
    dual_annotated = [
        a for a in articles
        if a.get("annotator_1_label") is not None and a.get("annotator_2_label") is not None
    ]

    if len(dual_annotated) < 50:
        result = {
            "status": "PENDING",
            "message": (
                f"Corpus contains {total} articles, but only {len(dual_annotated)} have completed dual-blind annotations. "
                f"A minimum of 50 dual annotations (target 1,000) is required for rigorous empirical kappa calculation. "
                "Empirical validation status: PENDING human review."
            ),
            "total_articles": total,
            "dual_annotated_count": len(dual_annotated),
            "cohens_kappa": None,
        }
        if output_report:
            _write_pending_report(output_report, result)
        return result

    l1 = [a["annotator_1_label"] for a in dual_annotated]
    l2 = [a["annotator_2_label"] for a in dual_annotated]
    metrics = compute_cohens_kappa(l1, l2)
    metrics["total_corpus_size"] = total
    metrics["dual_annotated_size"] = len(dual_annotated)

    if output_report:
        _write_completed_report(output_report, metrics)

    return metrics

def _write_pending_report(path: str, info: Dict[str, Any]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    md = f"""# Research Evaluation: Multi-Annotator Agreement (1,000-Article Corpus)

## Empirical Status: **PENDING INDEPENDENT HUMAN ANNOTATION**

### Academic Integrity Statement
In compliance with strict research governance and transparency standards, GeoSentinel AI **never fabricates synthetic human annotations or simulated Cohen's kappa scores**.

### Current Corpus Pipeline Status
- **Target Corpus Scale**: $\ge 1,000$ Real-World Geopolitical OSINT Articles
- **Articles Collected**: `{info.get('total_articles', 0)}`
- **Dual Blind Reviews Completed**: `{info.get('dual_annotated_count', 0)}`
- **Minimum Threshold for Formal Kappa**: 50 dual reviews (target: 1,000 dual reviews)
- **Target Cohen's Kappa**: $\kappa \ge 0.80$ (Substantial Agreement)
- **Status Notice**: {info.get('message', 'Awaiting dual-blind human review.')}

### Standardized Protocols & Infrastructure Established
1. **Annotation Guidelines**: Published in [`research/annotation/ANNOTATION_GUIDELINES.md`](../annotation/ANNOTATION_GUIDELINES.md)
2. **Standardized Schema**: Defined in [`research/annotation/schema.json`](../annotation/schema.json)
3. **Statistical Computation Engine**: Script [`research/annotation/compute_agreement.py`](../annotation/compute_agreement.py)
4. **Execution Command**:
   ```bash
   python research/annotation/compute_agreement.py --corpus research/annotation/corpus_1000.json
   ```
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)

def _write_completed_report(path: str, metrics: Dict[str, Any]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conf_str = "\n".join(str(row) for row in metrics.get("confusion_matrix", []))
    md = f"""# Research Evaluation: Multi-Annotator Agreement (1,000-Article Corpus)

## Empirical Status: **VERIFIED**

### Measured Agreement Metrics
- **Total Articles in Corpus**: `{metrics.get('total_corpus_size')}`
- **Dual-Annotated Sample Size**: `{metrics.get('dual_annotated_size')}`
- **Observed Agreement ($P_o$)**: `{metrics.get('observed_agreement')}`
- **Hypothetical Chance Agreement ($P_e$)**: `{metrics.get('chance_agreement')}`
- **Cohen's Kappa ($\kappa$)**: `{metrics.get('cohens_kappa')}`
- **Acceptance Threshold Met ($\kappa \ge 0.80$)**: `{'YES' if metrics.get('target_met') else 'NO'}`

### Inter-Annotator Agreement Matrix
Categories: `['CONFLICT', 'SECURITY', 'ECONOMY', 'DIPLOMACY']`
```
{conf_str}
```
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    base = os.path.dirname(__file__)
    corpus_p = os.path.join(base, "corpus_1000.json")
    report_p = os.path.join(base, "../evaluation/multi_annotator_agreement.md")
    res = evaluate_corpus_file(corpus_p, report_p)
    print(f"Agreement analysis complete. Status: {res.get('status')}")
