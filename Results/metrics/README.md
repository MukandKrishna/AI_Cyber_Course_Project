# Grouped Evaluation Outputs

This folder contains the grouped-evaluation CSV outputs and plots generated from `../../../src/evaluation/grouped_evaluation_pipeline.py` using `../../features/pair_level_features_enhanced.csv`.

The files cover the 5-fold folder-based split, baseline scores, model scores, and summary metrics used in the report.

Key files include the feature-column lists, fold assignments, baseline and model prediction tables, summary CSVs, and the full-vs-no-length comparison.

The main interpretation point is that several simple length-based baselines score perfectly on the current synthetic data, so the final report should treat that as a limitation rather than a deployment-ready result.
