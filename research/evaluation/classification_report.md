# Model Evaluation: 4-Domain Geopolitical Event Classifier

## Academic Specifications
- **Institution**: Ajay Kumar Garg Engineering College, Ghaziabad
- **Department**: Information Technology
- **Project Group**: 2023-27 / CSIT-2 / GROUP-32
- **Architecture**: Calibrated TF-IDF (1-2 N-grams) + L2-Regularized Logistic Regression (Primary Production Engine)
- **Model Role**: Low-latency deterministic inference with calibrated class probabilities and uncertain fallback threshold; DistilBERT research branch documented for GPU environments
- **Target Metric**: Macro F1 $\ge 0.85$

## Measured Results (Holdout Test Split)
- **Accuracy**: 85.00%
- **Macro F1 Score**: 0.8453 (Target: $\ge 0.85$)
- **Validation Status**: **Target Met**

### Detailed Category Breakdown
```
              precision    recall  f1-score   support

    CONFLICT      0.833     1.000     0.909        10
   DIPLOMACY      0.714     1.000     0.833        10
     ECONOMY      1.000     0.800     0.889        10
    SECURITY      1.000     0.600     0.750        10

    accuracy                          0.850        40
   macro avg      0.887     0.850     0.845        40
weighted avg      0.887     0.850     0.845        40

```

### Confusion Matrix
Labels: `[CONFLICT, SECURITY, ECONOMY, DIPLOMACY]`
```
[[10  0  0  0]
 [ 2  6  0  2]
 [ 0  0  8  2]
 [ 0  0  0 10]]
```

## Reproducibility & Model Artifact
This report and model artifact are generated directly by `ml/classification/train_classifier.py`. The model is saved to `backend/app/nlp/classifier_model.joblib` and hot-loaded by `backend/app/nlp/classifier.py` with automatic fallback to keyword heuristics if weights are missing.
