# Baseline Experiments Summary

## Objective

Evaluate simple non-trained heuristics under the same grouped 5-fold evaluation protocol that will later be used for Random Forest, SVM, and MLP models.

The purpose of these baselines is to provide a fair reference point before training machine learning models.

## Data Used

- Feature table: `outputs/features/pair_level_features_enhanced.csv`
- Sample unit: one central-node/contact-node pair
- Total samples: 110
- Positive samples: 10
- Negative samples: 100
- Evaluation grouping column: `folder`

## Evaluation Setup

Grouped 5-fold evaluation was used:

- each fold held out one complete `Dataset-*` folder
- each fold trained or scored on the remaining four folders
- each test fold contained 22 pair samples from 2 scenarios
- each test fold contained exactly 2 positive pairs

This avoids leakage between train and test splits because rows from the same dataset folder are never split across both sides.

## Baselines Tested

| Experiment | Scoring rule |
|---|---|
| `baseline_highest_message_count` | Select pair with highest message count |
| `baseline_longest_duration` | Select pair with longest interaction duration |
| `baseline_lowest_mean_length` | Select pair with lowest mean message length |
| `baseline_highest_evening_ratio` | Select pair with highest evening activity ratio |
| `baseline_highest_short_message_ratio` | Select pair with highest short-message ratio |
| `baseline_weighted_contextual_heuristic` | Weighted score using message count, duration, mean length, evening activity, short-message ratio, and late-night activity z-scores |

## Results

| Experiment | Top-1 Accuracy | MRR | Mean Positive Rank | F1 at Top-1 |
|---|---:|---:|---:|---:|
| `baseline_highest_message_count` | 0.00 | 0.3139 | 4.20 | 0.00 |
| `baseline_longest_duration` | 0.30 | 0.5767 | 2.70 | 0.30 |
| `baseline_lowest_mean_length` | 1.00 | 1.0000 | 1.00 | 1.00 |
| `baseline_highest_evening_ratio` | 0.50 | 0.6302 | 3.90 | 0.50 |
| `baseline_highest_short_message_ratio` | 1.00 | 1.0000 | 1.00 | 1.00 |
| `baseline_weighted_contextual_heuristic` | 1.00 | 1.0000 | 1.00 | 1.00 |

Detailed fold-level results are saved in:

- `outputs/metrics/grouped_evaluation/baseline_fold_metrics.csv`
- `outputs/metrics/grouped_evaluation/baseline_metrics_summary.csv`
- `outputs/metrics/grouped_evaluation/baseline_predictions_by_fold.csv`

## Analysis

The baseline results show that simple volume-based assumptions are not enough. The highest-message-count heuristic never ranked the true pair first, and the longest-duration heuristic only achieved 0.30 Top-1 Accuracy.

Message-length based baselines performed extremely strongly. Both the lowest mean message length and highest short-message ratio baselines ranked the true pair first in every scenario.

This is useful evidence, but it must be interpreted carefully. Because PASYDA is a synthetic metadata dataset, the perfect performance of message-length heuristics may indicate that the synthetic generation process created a strong artefact around message length. The final report should not claim that real-world grooming can be detected from message length alone.

The weighted contextual heuristic also performed perfectly, but this result is largely driven by the same message-length signal. It should be used as a strong baseline for comparison with ML models, while also being discussed as evidence of possible synthetic-data bias.

## Report Wording

The baseline experiments demonstrate that the task cannot be solved by communication volume alone. However, message-length features show unusually strong predictive value in the PASYDA metadata. This supports including message-length features in the main models, but it also motivates an ablation experiment without message-length features to test whether model performance depends too heavily on a synthetic artefact.
