# MLP with Contextual Features

## Experiment No

EXP-10

## Date

2026-06-09

## Name

Small MLP contextual-feature model

## Objective

Evaluate the lightweight MLP using enhanced contextual and sequence-derived features.

## Tools Used

Python, pandas, scikit-learn MLPClassifier

## Data Used

outputs/features/pair_level_features_enhanced.csv

## Procedure

The same MLP architecture and fold-safe oversampling approach were used with the enhanced feature table.

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

The contextual MLP achieves perfect performance. However, this should be interpreted alongside the message-length baseline and ablation results.

The result should be interpreted with the broader portfolio findings: message-length features are unusually predictive in PASYDA, and false-positive/false-negative risks remain important even when aggregate metrics are high.
