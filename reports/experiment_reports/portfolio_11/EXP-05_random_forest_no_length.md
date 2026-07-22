# Random Forest without Message-Length Features

## Experiment No

EXP-05

## Date

2026-06-09

## Name

Random Forest no-length ablation

## Objective

Test whether Random Forest performance depends on message-length-derived features.

## Tools Used

Python, pandas, scikit-learn RandomForestClassifier

## Data Used

outputs/features/pair_level_features_enhanced.csv with length-derived columns removed

## Procedure

All message-length-related features were removed, leaving 36 numeric features. The Random Forest was retrained using the same grouped folds.

Grouped 5-fold evaluation was used. Each fold held out one complete dataset folder and evaluated on the two scenarios inside that folder. Folds were not treated as separate experiments; fold metrics were aggregated for this report.

## Results

| Metric | Mean across folds |
|---|---:|
| Top-1 Accuracy | 0.7000 |
| Mean Reciprocal Rank | 0.7950 |
| Precision at Top-1 | 0.7000 |
| Recall at Top-1 | 0.7000 |
| F1 at Top-1 | 0.7000 |
| ROC-AUC | 0.9600 |
| PR-AUC | 0.8400 |

Detailed fold-level results are available in `outputs/metrics/grouped_evaluation`.

## Analysis of Results

Performance drops compared with the full feature set. This shows that the Random Forest relies strongly on message-length signals and supports the synthetic-shortcut limitation discussion.

The result should be interpreted with the broader portfolio findings: message-length features are unusually predictive in PASYDA, and false-positive/false-negative risks remain important even when aggregate metrics are high.
