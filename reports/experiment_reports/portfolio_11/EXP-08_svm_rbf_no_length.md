# SVM without Message-Length Features

## Experiment No

EXP-08

## Date

2026-06-09

## Name

SVM no-length ablation

## Objective

Test whether SVM performance remains robust when message-length-derived features are removed.

## Tools Used

Python, pandas, scikit-learn SVC

## Data Used

outputs/features/pair_level_features_enhanced.csv with length-derived columns removed

## Procedure

The no-length feature set was used with the same imputation, scaling, class weighting, and grouped folds as the full SVM model.

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

The SVM remains perfect without message-length features, suggesting that other contextual variables still separate the labelled pairs in PASYDA.

The result should be interpreted with the broader portfolio findings: message-length features are unusually predictive in PASYDA, and false-positive/false-negative risks remain important even when aggregate metrics are high.
