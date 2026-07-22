# Portfolio Experiment Index

| Experiment No | Experiment | Top-1 | MRR | F1 | ROC-AUC | PR-AUC |
|---|---|---:|---:|---:|---:|---:|
| EXP-01 | Heuristic Baseline: Highest Message Count | 0.0000 | 0.3139 | 0.0000 | 0.6800 | 0.2630 |
| EXP-02 | Heuristic Baseline: Lowest Mean Message Length | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| EXP-03 | Random Forest with Base Features | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| EXP-04 | Random Forest with Contextual Features | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| EXP-05 | Random Forest without Message-Length Features | 0.7000 | 0.7950 | 0.7000 | 0.9600 | 0.8400 |
| EXP-06 | SVM with Base Features | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| EXP-07 | SVM with Contextual Features | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| EXP-08 | SVM without Message-Length Features | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| EXP-09 | MLP with Base Features | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| EXP-10 | MLP with Contextual Features | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| EXP-11 | MLP without Message-Length Features | 0.9000 | 0.9111 | 0.9000 | 0.9300 | 0.9125 |

## Notes

- Each report describes one experiment configuration.
- The 5 grouped folds are internal evaluation repeats, not separate experiment reports.
- Full-feature models achieve perfect performance, but no-length ablations are included to test synthetic shortcut risk.
- False alerts and missed detections are discussed in `../error_and_false_alert_discussion.md`.
