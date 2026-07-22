# Random Forest with Contextual Features

## Experiment No

EXP-04

## Date

2026-06-09

## Name

Random Forest contextual-feature model

## Objective

Evaluate Random Forest performance after adding contextual ranks, z-scores, and sequence-derived features.

## Tools Used

Python, pandas, scikit-learn RandomForestClassifier

## Data Used

outputs/features/pair_level_features_enhanced.csv

## Procedure

The same Random Forest configuration was trained using the enhanced contextual feature table and the same grouped 5-fold split.

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

The contextual Random Forest also achieves perfect performance. Because the base model was already perfect, contextual features do not improve headline metrics but provide richer explanatory evidence.

The result should be interpreted with the broader portfolio findings: message-length features are unusually predictive in PASYDA, and false-positive/false-negative risks remain important even when aggregate metrics are high.
