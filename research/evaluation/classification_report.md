# Model Evaluation: 4-Domain Geopolitical Event Classifier

## Academic Specifications
- **Institution**: Ajay Kumar Garg Engineering College, Ghaziabad
- **Department**: Information Technology
- **Project Group**: 2023-27 / CSIT-2 / GROUP-32
- **Architecture**: DistilBERT Base Sequence Classifier Head / TF-IDF N-Gram Logistic Baseline
- **Target Metric**: Macro F1 $\ge 0.85$

## Measured Results (Holdout Test Split)
- **Accuracy**: 100.00%
- **Macro F1 Score**: 1.0000 (Target: $\ge 0.85$)
- **Validation Status**: **Target Met**

### Detailed Category Breakdown
```
              precision    recall  f1-score   support

    CONFLICT      1.000     1.000     1.000         6
   DIPLOMACY      1.000     1.000     1.000         6
     ECONOMY      1.000     1.000     1.000         6
    SECURITY      1.000     1.000     1.000         6

    accuracy                          1.000        24
   macro avg      1.000     1.000     1.000        24
weighted avg      1.000     1.000     1.000        24

```

### Confusion Matrix
Labels: `[CONFLICT, SECURITY, ECONOMY, DIPLOMACY]`
```
[[6 0 0 0]
 [0 6 0 0]
 [0 0 6 0]
 [0 0 0 6]]
```

## Reproducibility Note
This report and model artifact are generated directly by `ml/classification/train_classifier.py`. The model is saved to `backend/app/nlp/classifier_model.joblib` and hot-loaded by the backend NLP pipeline.
