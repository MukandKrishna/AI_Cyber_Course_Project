# No-Length Feature Ablation Experiment

## Experiment No

ABL-01

## Objective

Test whether model performance depends too heavily on message-length features.

This ablation is important because the full-feature models and several simple baselines achieved perfect scores. Removing message-length features checks whether the models are learning broader behavioural signals or relying on a synthetic shortcut.

## Tools Used

- Python
- pandas
- scikit-learn
- grouped 5-fold evaluation pipeline

## Data Used

- Input table: `outputs/features/pair_level_features_enhanced.csv`
- Full feature set: 49 numeric features
- No-length feature set: 36 numeric features
- Removed features: 13 message-length-related features
- Split: grouped 5-fold evaluation by `folder`

## Removed Features

- `mean_length`
- `median_length`
- `std_length`
- `min_length`
- `max_length`
- `short_message_ratio`
- `mean_length_rank_in_scenario`
- `mean_length_pct_rank_in_scenario`
- `short_message_ratio_rank_in_scenario`
- `short_message_ratio_pct_rank_in_scenario`
- `mean_length_z_in_scenario`
- `median_length_z_in_scenario`
- `short_message_ratio_z_in_scenario`

## Procedure

The Random Forest, SVM, and MLP models were retrained using the same grouped folds as the full-feature experiments. The only change was that all message-length-derived features were removed before fitting the models.

All preprocessing remained fold-safe:

- training folders only were used to fit imputers and scalers
- the held-out dataset folder was only used for testing
- no scenario or folder was split across train and test within a fold

## Results

| Model | Full Top-1 | No-Length Top-1 | Top-1 Drop | Full MRR | No-Length MRR | Full F1 | No-Length F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Random Forest | 1.00 | 0.70 | 0.30 | 1.0000 | 0.7950 | 1.00 | 0.70 |
| SVM | 1.00 | 1.00 | 0.00 | 1.0000 | 1.0000 | 1.00 | 1.00 |
| MLP | 1.00 | 0.90 | 0.10 | 1.0000 | 0.9111 | 1.00 | 0.90 |

Detailed outputs:

- `outputs/metrics/grouped_evaluation/model_metrics_summary.csv`
- `outputs/metrics/grouped_evaluation/model_fold_metrics.csv`
- `outputs/metrics/grouped_evaluation/full_vs_no_length_comparison.csv`
- `outputs/metrics/grouped_evaluation/feature_columns_removed_for_no_length_ablation.csv`

## Fold-Level Observations

The Random Forest no-length model dropped below perfect performance in Dataset-1, Dataset-3, and Dataset-4.

The MLP no-length model dropped in Dataset-3 only.

The SVM no-length model remained perfect across all five held-out dataset folders.

## Analysis

The ablation confirms that message-length features are important, but not the only possible signal in the dataset.

Random Forest performance dropped from 1.00 to 0.70 Top-1 Accuracy, showing that this model relied strongly on length-related predictors.

The MLP dropped from 1.00 to 0.90 Top-1 Accuracy, suggesting moderate dependence on length features but better recovery from other contextual variables.

The SVM remained at 1.00 Top-1 Accuracy, suggesting that the remaining behavioural features still separate the positive and negative pairs under the current grouped evaluation setup.

This makes the final interpretation more balanced. The full-feature performance is strong, but the ablation shows that some of the result is driven by message-length patterns, which may be an artefact of the synthetic PASYDA generation process.

## Conclusion

The no-length ablation strengthens the project because it directly tests whether the models are exploiting a shortcut. The results show partial dependence on message-length features, especially for Random Forest, while SVM remains robust on the remaining contextual features.

The final report should present the full-feature results as successful on PASYDA, but should also state that real-world generalisation is uncertain because message-length cues may not transfer reliably outside the synthetic dataset.
