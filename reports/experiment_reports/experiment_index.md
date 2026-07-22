# Experiment Index

## Dataset and Evaluation

- Modelling table: `outputs/features/pair_level_features_enhanced.csv`
- Evaluation split: grouped 5-fold by `folder`
- Metrics: Top-1 Accuracy, MRR, Precision at Top-1, Recall at Top-1, F1 at Top-1, ROC-AUC, PR-AUC

## Experiment Reports

The assignment-style individual experiment reports are in:

`reports/experiment_reports/portfolio_11`

| Experiment ID | Report                                  | Objective                                                      | Main Output                                                                    |
| ------------- | --------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| BASE-01       | `baseline_experiments_summary.md`     | Compare simple non-trained heuristics                          | Message-length baselines perform perfectly; volume-only baseline fails         |
| MODEL-01      | `model_experiments_summary.md`        | Train RF, SVM, and MLP on enhanced features                    | All three models achieve perfect grouped-evaluation results                    |
| ABL-01        | `no_length_ablation_experiment.md`    | Remove message-length features and retrain models              | RF drops to 0.70 Top-1, MLP drops to 0.90, SVM remains 1.00                    |
| ERR-01        | `error_and_false_alert_discussion.md` | Discuss false positives, false negatives, and deployment risks | High scores must be interpreted cautiously due to synthetic-data shortcut risk |

The experiments show that the engineered feature table is highly predictive on PASYDA. But the perfect full-feature results are not enough by themselves. The baselines and ablation show that message-length features are unusually strong, which may reflect a synthetic dataset artefact.
