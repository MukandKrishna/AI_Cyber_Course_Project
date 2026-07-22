# Model Experiments Summary

## Objective

Train and evaluate the required model families using the same enhanced feature table, grouped folds, and ranking metrics:

- Random Forest
- SVM
- small MLP

## Data Used

- Feature table: `outputs/features/pair_level_features_enhanced.csv`
- Modelling features: 49 numeric columns
- Sample unit: one central-node/contact-node pair
- Total samples: 110
- Positive samples: 10
- Negative samples: 100
- Grouping column: `folder`

## Evaluation Setup

The models were evaluated using grouped 5-fold evaluation by dataset folder.

Each fold:

- trained on 4 complete dataset folders
- tested on 1 held-out dataset folder
- used 88 training rows and 22 test rows
- included 8 positive training pairs and 2 positive test pairs

This split avoids leakage because no dataset folder appears in both training and test data within the same fold.

## Models

| Experiment | Model | Notes |
|---|---|---|
| `random_forest_enhanced` | Random Forest | 300 trees, shallow depth, balanced class weights |
| `svm_rbf_enhanced` | SVM | RBF kernel, standardized features, balanced class weights |
| `mlp_small_enhanced` | MLP | 32 -> 16 hidden units, standardized features, positive-class oversampling within training folds |

## Results

| Experiment | Top-1 Accuracy | MRR | Mean Positive Rank | F1 at Top-1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|---:|
| `random_forest_enhanced` | 1.00 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 |
| `svm_rbf_enhanced` | 1.00 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 |
| `mlp_small_enhanced` | 1.00 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.00 |

## No-Length Ablation Results

| Experiment | Top-1 Accuracy | MRR | Mean Positive Rank | F1 at Top-1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|---:|
| `random_forest_no_length` | 0.70 | 0.7950 | 1.80 | 0.70 | 0.96 | 0.8400 |
| `svm_rbf_no_length` | 1.00 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.0000 |
| `mlp_small_no_length` | 0.90 | 0.9111 | 1.80 | 0.90 | 0.93 | 0.9125 |

Detailed outputs are saved in:

- `outputs/metrics/grouped_evaluation/model_fold_metrics.csv`
- `outputs/metrics/grouped_evaluation/model_metrics_summary.csv`
- `outputs/metrics/grouped_evaluation/model_predictions_by_fold.csv`
- `outputs/metrics/grouped_evaluation/all_metrics_summary.csv`
- `outputs/metrics/grouped_evaluation/full_vs_no_length_comparison.csv`

## Analysis

All three model families ranked the true pair first in every held-out scenario. This means the enhanced feature table contains enough signal for Random Forest, SVM, and MLP models to solve the grouped evaluation task on the PASYDA dataset.

However, the result should be interpreted carefully. Earlier baseline experiments showed that message-length features alone also achieved perfect performance. Therefore, the model results are strong, but they may be heavily influenced by a synthetic message-length artefact in the dataset.

The no-length ablation supports this concern. Random Forest dropped from 1.00 to 0.70 Top-1 Accuracy, and the MLP dropped from 1.00 to 0.90. SVM remained perfect, suggesting that some non-length contextual features still separate the classes, but the overall evidence shows that length-related features are a major part of the predictive signal.

The most academically defensible interpretation is:

- grouped evaluation was implemented correctly
- all required model families were trained under the same protocol
- the enhanced feature representation is highly predictive on PASYDA
- the dataset may contain a strong synthetic shortcut, especially around message length
- ablation experiments without message-length features show partial dependence on message-length signals

## Report Wording

Random Forest, SVM, and a lightweight MLP were evaluated using the same grouped 5-fold split by dataset folder. All three models achieved perfect ranking performance on the enhanced feature set, identifying the true pair as rank 1 in every held-out scenario. However, no-length ablation reduced Random Forest and MLP performance, and simple message-length heuristics also performed perfectly. This suggests that the PASYDA synthetic metadata may contain strong artefacts, so model performance should be presented as successful on this dataset but not automatically generalizable to real-world grooming detection.
