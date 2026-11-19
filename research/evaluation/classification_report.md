# Model Evaluation: 4-Domain Geopolitical Event Classifier

## Academic Specifications
- **Institution**: Ajay Kumar Garg Engineering College, Ghaziabad
- **Department**: Information Technology
- **Project Group**: 2023-27 / CSIT-2 / GROUP-32
- **Architecture**: Calibrated TF-IDF (1-2 N-grams) + L2-Regularized Logistic Regression (Primary Production Engine)
- **Model Role**: Low-latency deterministic inference with calibrated class probabilities and uncertain fallback threshold; DistilBERT research branch documented for GPU environments
- **Target Metric**: Macro F1 $\ge 0.85$

## Measured Results (Holdout Test Split)
- **Accuracy**: 86.67%
- **Macro F1 Score**: 0.8676 (Target: $\ge 0.85$)
- **Validation Status**: **Target Met**

### Detailed Category Breakdown
```
              precision    recall  f1-score   support

    CONFLICT      0.688     1.000     0.815        11
   DIPLOMACY      0.917     1.000     0.957        11
     ECONOMY      1.000     0.750     0.857        12
    SECURITY      1.000     0.727     0.842        11

    accuracy                          0.867        45
   macro avg      0.901     0.869     0.868        45
weighted avg      0.903     0.867     0.867        45

```

### Confusion Matrix
Labels: `[CONFLICT, SECURITY, ECONOMY, DIPLOMACY]`
```
[[11  0  0  0]
 [ 3  8  0  0]
 [ 2  0  9  1]
 [ 0  0  0 11]]
```

## Reproducibility & Model Artifact
This report and model artifact are generated directly by `ml/classification/train_classifier.py`. The model is saved to `backend/app/nlp/classifier_model.joblib` and hot-loaded by `backend/app/nlp/classifier.py` with automatic fallback to keyword heuristics if weights are missing.
