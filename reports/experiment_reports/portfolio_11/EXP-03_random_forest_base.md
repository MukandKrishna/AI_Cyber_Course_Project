# Random Forest with Base Features

## Experiment No

EXP-03

## Date

2026-06-09

## Name

Random Forest base-feature model

## Objective

Evaluate Random Forest performance using the frozen base pair-level feature table.

## Tools Used

Python, pandas, scikit-learn RandomForestClassifier

## Data Used

outputs/features/pair_level_features_base_frozen.csv

## Procedure

A Random Forest with 300 trees, shallow max depth, minimum leaf size of 2, and balanced class weights was trained in each grouped fold. Each fold held out one complete dataset folder.

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

The model achieves perfect grouped-evaluation performance with base pair-level features, indicating that the original engineered variables already contain strong discriminative signal.

The result should be interpreted with the broader portfolio findings: message-length features are unusually predictive in PASYDA, and false-positive/false-negative risks remain important even when aggregate metrics are high.
