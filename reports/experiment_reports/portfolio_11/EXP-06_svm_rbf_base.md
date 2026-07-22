# SVM with Base Features

## Experiment No

EXP-06

## Date

2026-06-09

## Name

SVM base-feature model

## Objective

Evaluate an RBF-kernel SVM using the frozen base feature table.

## Tools Used

Python, pandas, scikit-learn SVC

## Data Used

outputs/features/pair_level_features_base_frozen.csv

## Procedure

A pipeline with median imputation, standard scaling, and class-balanced RBF SVM was trained in each grouped fold.

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

The SVM achieves perfect performance on base features, showing that the class boundary is separable with the original pair-level variables.

The result should be interpreted with the broader portfolio findings: message-length features are unusually predictive in PASYDA, and false-positive/false-negative risks remain important even when aggregate metrics are high.
