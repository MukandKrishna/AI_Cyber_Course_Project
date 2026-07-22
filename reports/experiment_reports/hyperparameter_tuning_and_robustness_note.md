# Hyperparameter Tuning and Robustness Note

## Purpose

The marking criteria specifically asks for systematic hyperparameter tuning rather than ad hoc model choices. Because the full-feature models already achieved perfect scores, the goal of this step was not to chase a higher result. The goal was to show that model settings were checked in a leakage-safe way.

## Method

A compact nested grouped-validation procedure was added in:

`src/evaluation/hyperparameter_tuning_analysis.py`

For each outer fold:

- one complete dataset folder was held out for final testing
- the remaining four folders were used for inner grouped validation
- candidate hyperparameters were compared on the inner validation folders
- the selected configuration was then retrained on the four outer training folders
- the selected model was evaluated on the untouched outer test folder

This avoids using the held-out test folder to choose hyperparameters.

## Candidate Settings Tested

Random Forest:

- `rf_depth3_leaf2`
- `rf_depth4_leaf2`
- `rf_depthNone_leaf1`

SVM:

- `svm_C0.1`
- `svm_C1`
- `svm_C10`

MLP:

- `mlp_16_alpha0.01`
- `mlp_32_16_alpha0.01`
- `mlp_32_16_alpha0.001`

## Outputs

- `outputs/metrics/grouped_evaluation/tuning_inner_scores.csv`
- `outputs/metrics/grouped_evaluation/tuning_selected_configs_by_outer_fold.csv`
- `outputs/metrics/grouped_evaluation/tuning_outer_test_metrics.csv`
- `outputs/metrics/grouped_evaluation/tuning_summary.csv`

## Results

The nested tuning procedure achieved:

| Model | Tuned Top-1 | Tuned MRR | Tuned F1 | Tuned ROC-AUC | Tuned PR-AUC |
|---|---:|---:|---:|---:|---:|
| Random Forest | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| SVM | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| MLP | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

## Interpretation

The tuning results support the conclusion that the full-feature task is easy to separate under grouped evaluation. However, this should not be overstated, because the dataset has only 10 positive pair-level samples and message-length baselines also perform perfectly.

The strongest academic interpretation is:

- hyperparameters were checked systematically
- full-feature performance is stable across reasonable configurations
- no-length ablation remains essential for robustness analysis
- high scores should still be framed cautiously due to synthetic-data shortcut risk

