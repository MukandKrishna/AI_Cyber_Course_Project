# MLP with Base Features

## Experiment No

EXP-09

## Date

2026-06-09

## Name

Small MLP base-feature model

## Objective

Evaluate a lightweight deep learning model on the frozen base pair-level features.

## Tools Used

Python, pandas, scikit-learn MLPClassifier

## Data Used

outputs/features/pair_level_features_base_frozen.csv

## Procedure

A small MLP with 32 and 16 hidden units was trained with median imputation, standard scaling, and positive-class oversampling inside training folds only.

Grouped 5-fold evaluation was used. Each fold held out one complete dataset folder and evaluated on the two scenarios inside that folder. Folds were not treated as separate experiments; fold metrics were aggregated for this report.

## Results

| Metric | Mean across folds |
|---|---:|
| Top-1 Accuracy | 1.0000 |
| Mean Reciprocal Rank | 1.0000 |
| Precision at Top-1 | 1.0000 |
| Recall at Top-1 | 1.0000 |
| F1 at Top-1 | 1.0000 |
| ROC-AUC | 1.0000 |
| PR-AUC | 1.0000 |

Detailed fold-level results are available in `outputs/metrics/grouped_evaluation`.

## Analysis of Results

The MLP achieves perfect performance on base features. The result confirms that a lightweight tabular deep model is sufficient for this small engineered-feature dataset.

The result should be interpreted with the broader portfolio findings: message-length features are unusually predictive in PASYDA, and false-positive/false-negative risks remain important even when aggregate metrics are high.
