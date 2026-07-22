# Error and False-Alert Discussion

## Why Accuracy Alone Is Not Enough

Online grooming detection is a high-risk cyber-safety task. A model with high accuracy can still be unsafe if it produces false alerts or misses true grooming cases.

In this project, each scenario contains 11 candidate pairs and only one true positive. This means a model must rank the correct pair first, not merely classify many negative pairs correctly. For that reason, Top-1 Accuracy and Mean Reciprocal Rank are more informative than ordinary row-level accuracy.

## False Positives

A false positive occurs when the model incorrectly identifies a non-grooming contact pair as the grooming-related pair.

Possible consequences:

- innocent users may be wrongly flagged
- investigators may waste time reviewing irrelevant pairs
- trust in the detection system may decrease
- over-sensitive models may create too many alerts for practical use

This is why Precision at Top-1 is important. It measures whether the pair selected as the highest-risk pair is actually the true pair.

## False Negatives

A false negative occurs when the true grooming pair is not ranked first or is missed by the model.

Possible consequences:

- a harmful interaction may not be escalated
- safeguarding action may be delayed
- the model may create a false sense of security

This is why Recall at Top-1 and Mean Reciprocal Rank are important. If the true pair is not ranked first, MRR still shows whether it was near the top or buried lower in the candidate list.

## What the Current Results Show

With the full enhanced feature set, Random Forest, SVM, and MLP all achieved perfect performance:

- Top-1 Accuracy = 1.00
- Precision at Top-1 = 1.00
- Recall at Top-1 = 1.00
- F1 at Top-1 = 1.00
- MRR = 1.00

This means no false positives or false negatives occurred under the grouped evaluation setup.

However, this should not be overclaimed. The dataset is synthetic, small, and contains only 10 positive pair-level samples. Simple message-length baselines also achieved perfect performance, suggesting that the dataset may contain a strong shortcut.

## What the Ablation Adds

The no-length ablation gives a more realistic view of model robustness:

- Random Forest dropped to 0.70 Top-1 Accuracy
- MLP dropped to 0.90 Top-1 Accuracy
- SVM remained at 1.00 Top-1 Accuracy

This means that when message-length cues are removed, some models begin making top-rank errors. These errors represent possible false alerts, because the model selects the wrong pair as the most suspicious pair in a held-out scenario.

Actual no-length error summary:

| Model | True pairs tested | Top-1 misses | Worst true-pair rank | Mean true-pair rank |
|---|---:|---:|---:|---:|
| Random Forest no-length | 10 | 3 | 5 | 1.8 |
| MLP no-length | 10 | 1 | 9 | 1.8 |
| SVM no-length | 10 | 0 | 1 | 1.0 |

The specific failed held-out cases were:

- Random Forest no-length missed `perp_1` in `Dataset-1`
- Random Forest no-length missed `perp_4` in `Dataset-3`
- Random Forest no-length missed `perp_6` in `Dataset-4`
- MLP no-length missed `perp_4` in `Dataset-3`

The most difficult shared case was `perp_4`, where both Random Forest and MLP failed once length-derived features were removed. This suggests that some scenarios depend more heavily on message-length cues, while others remain separable using timing, directionality, and contextual rank features.

The ablation therefore supports a cautious conclusion:

The full-feature models perform extremely well on PASYDA, but part of the performance depends on message-length patterns that may not generalise to real-world grooming detection.

## Practical Deployment Considerations

If this system were used outside the synthetic dataset, it should not automatically accuse or classify users. A safer use would be decision support:

- rank candidate pairs for human review
- provide explainable feature evidence
- avoid fully automated enforcement decisions
- tune thresholds to reduce false alerts
- monitor false positives and false negatives after deployment
- retrain or recalibrate using real-world validated data

## Recommended Report Wording

Although the full-feature models achieved perfect grouped-evaluation scores, accuracy alone is not sufficient for a grooming-detection system. False positives could wrongly flag innocent communication, while false negatives could miss genuinely harmful interactions. The no-length ablation showed that some models made errors when message-length features were removed, suggesting that the original perfect scores may partly rely on synthetic metadata artefacts. Therefore, the models should be interpreted as successful on PASYDA but not yet validated for real-world deployment without additional data, error analysis, and human-in-the-loop safeguards.
