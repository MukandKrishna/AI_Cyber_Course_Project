# SVM with Contextual Features

## Experiment No

EXP-07

## Date

2026-06-09

## Name

SVM contextual-feature model

## Objective

Evaluate the RBF-kernel SVM with enhanced contextual features.

## Tools Used

Python, pandas, scikit-learn SVC

## Data Used

outputs/features/pair_level_features_enhanced.csv

## Procedure

The same SVM preprocessing and model setup was trained using the enhanced feature table under grouped 5-fold evaluation.

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

The contextual SVM achieves perfect performance. Together with the ablation result, this suggests the SVM can exploit both length and non-length contextual signals.

The result should be interpreted with the broader portfolio findings: message-length features are unusually predictive in PASYDA, and false-positive/false-negative risks remain important even when aggregate metrics are high.
