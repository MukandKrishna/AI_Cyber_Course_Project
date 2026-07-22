# Heuristic Baseline: Highest Message Count

## Experiment No

EXP-01

## Date

2026-06-09

## Name

Highest message count baseline

## Objective

Test whether the true grooming-related pair can be found by selecting the candidate pair with the highest communication volume.

## Tools Used

Python, pandas, grouped evaluation pipeline

## Data Used

outputs/features/pair_level_features_enhanced.csv

## Procedure

For each held-out scenario, candidate pairs were ranked by message_count in descending order. The top-ranked pair was treated as the predicted grooming-related pair. The same grouped 5-fold split by dataset folder was used.

Grouped 5-fold evaluation was used. Each fold held out one complete dataset folder and evaluated on the two scenarios inside that folder. Folds were not treated as separate experiments; fold metrics were aggregated for this report.

## Results

| Metric | Mean across folds |
|---|---:|
| Top-1 Accuracy | 0.0000 |
| Mean Reciprocal Rank | 0.3139 |
| Precision at Top-1 | 0.0000 |
| Recall at Top-1 | 0.0000 |
| F1 at Top-1 | 0.0000 |
| ROC-AUC | 0.6800 |
| PR-AUC | 0.2630 |

Detailed fold-level results are available in `outputs/metrics/grouped_evaluation`.

## Analysis of Results

This baseline tests a simple assumption: grooming pairs may communicate more frequently than ordinary pairs. Its weak Top-1 result shows that communication volume alone is not a reliable detector in this dataset.

The result should be interpreted with the broader portfolio findings: message-length features are unusually predictive in PASYDA, and false-positive/false-negative risks remain important even when aggregate metrics are high.
