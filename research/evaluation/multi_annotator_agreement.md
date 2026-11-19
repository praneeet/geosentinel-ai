# Research Evaluation: Multi-Annotator Agreement (1,000-Article Corpus)

## Empirical Status: **PENDING INDEPENDENT HUMAN ANNOTATION**

### Academic Integrity Statement
In compliance with strict research governance and transparency standards, GeoSentinel AI **never fabricates synthetic human annotations or simulated Cohen's kappa scores**.

### Current Corpus Pipeline Status
- **Target Corpus Scale**: $\ge 1,000$ Real-World Geopolitical OSINT Articles
- **Articles Collected**: `0`
- **Dual Blind Reviews Completed**: `0`
- **Minimum Threshold for Formal Kappa**: 50 dual reviews (target: 1,000 dual reviews)
- **Target Cohen's Kappa**: $\kappa \ge 0.80$ (Substantial Agreement)
- **Status Notice**: Corpus file not found at E:\GeoSentinel AI\research\annotation\corpus_1000.json. Empirical multi-annotator review pending.

### Standardized Protocols & Infrastructure Established
1. **Annotation Guidelines**: Published in [`research/annotation/ANNOTATION_GUIDELINES.md`](../annotation/ANNOTATION_GUIDELINES.md)
2. **Standardized Schema**: Defined in [`research/annotation/schema.json`](../annotation/schema.json)
3. **Statistical Computation Engine**: Script [`research/annotation/compute_agreement.py`](../annotation/compute_agreement.py)
4. **Execution Command**:
   ```bash
   python research/annotation/compute_agreement.py --corpus research/annotation/corpus_1000.json
   ```
