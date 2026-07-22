# MLP without Message-Length Features

## Experiment No

EXP-11

## Date

2026-06-09

## Name

Small MLP no-length ablation

## Objective

Test whether the MLP remains robust after removing message-length-derived features.

## Tools Used

Python, pandas, scikit-learn MLPClassifier

## Data Used

outputs/features/pair_level_features_enhanced.csv with length-derived columns removed

## Procedure

The MLP was retrained on the 36-feature no-length table using the same grouped folds and training-fold-only positive oversampling.

Grouped 5-fold evaluation was used. Each fold held out one complete dataset folder and evaluated on the two scenarios inside that folder. Folds were not treated as separate experiments; fold metrics were aggregated for this report.

## Results

| Metric | Mean across folds |
|---|---:|
| Top-1 Accuracy | 0.9000 |
| Mean Reciprocal Rank | 0.9111 |
| Precision at Top-1 | 0.9000 |
| Recall at Top-1 | 0.9000 |
| F1 at Top-1 | 0.9000 |
| ROC-AUC | 0.9300 |
| PR-AUC | 0.9125 |

Detailed fold-level results are available in `outputs/metrics/grouped_evaluation`.

## Analysis of Results

Performance drops slightly compared with the full feature set. This indicates some dependence on length-related signals, but the MLP still retains strong performance from other contextual features.

The result should be interpreted with the broader portfolio findings: message-length features are unusually predictive in PASYDA, and false-positive/false-negative risks remain important even when aggregate metrics are high.
