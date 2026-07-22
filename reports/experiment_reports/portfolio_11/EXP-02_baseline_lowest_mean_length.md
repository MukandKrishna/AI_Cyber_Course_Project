# Heuristic Baseline: Lowest Mean Message Length

## Experiment No

EXP-02

## Date

2026-06-09

## Name

Lowest mean message length baseline

## Objective

Test whether message brevity alone can identify the true grooming-related pair.

## Tools Used

Python, pandas, grouped evaluation pipeline

## Data Used

outputs/features/pair_level_features_enhanced.csv

## Procedure

For each held-out scenario, candidate pairs were ranked by mean_length in ascending order. The shortest average-message pair was treated as the predicted grooming-related pair.

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

This baseline performs perfectly, which is useful but also concerning. It suggests that PASYDA may contain a strong synthetic message-length artefact. The result justifies later no-length ablation experiments.

The result should be interpreted with the broader portfolio findings: message-length features are unusually predictive in PASYDA, and false-positive/false-negative risks remain important even when aggregate metrics are high.
