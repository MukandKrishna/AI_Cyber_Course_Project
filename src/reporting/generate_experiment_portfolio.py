from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
METRICS_DIR = PROJECT_ROOT / "outputs" / "metrics" / "grouped_evaluation"
REPORT_DIR = PROJECT_ROOT / "reports" / "experiment_reports" / "portfolio_11"


EXPERIMENTS = [
    {
        "id": "EXP-01",
        "title": "Heuristic Baseline: Highest Message Count",
        "experiment": "baseline_highest_message_count",
        "name": "Highest message count baseline",
        "objective": "Test whether the true grooming-related pair can be found by selecting the candidate pair with the highest communication volume.",
        "tools": "Python, pandas, grouped evaluation pipeline",
        "data": "outputs/features/pair_level_features_enhanced.csv",
        "procedure": "For each held-out scenario, candidate pairs were ranked by message_count in descending order. The top-ranked pair was treated as the predicted grooming-related pair. The same grouped 5-fold split by dataset folder was used.",
        "analysis": "This baseline tests a simple assumption: grooming pairs may communicate more frequently than ordinary pairs. Its weak Top-1 result shows that communication volume alone is not a reliable detector in this dataset.",
    },
    {
        "id": "EXP-02",
        "title": "Heuristic Baseline: Lowest Mean Message Length",
        "experiment": "baseline_lowest_mean_length",
        "name": "Lowest mean message length baseline",
        "objective": "Test whether message brevity alone can identify the true grooming-related pair.",
        "tools": "Python, pandas, grouped evaluation pipeline",
        "data": "outputs/features/pair_level_features_enhanced.csv",
        "procedure": "For each held-out scenario, candidate pairs were ranked by mean_length in ascending order. The shortest average-message pair was treated as the predicted grooming-related pair.",
        "analysis": "This baseline performs perfectly, which is useful but also concerning. It suggests that PASYDA may contain a strong synthetic message-length artefact. The result justifies later no-length ablation experiments.",
    },
    {
        "id": "EXP-03",
        "title": "Random Forest with Base Features",
        "experiment": "random_forest_base",
        "name": "Random Forest base-feature model",
        "objective": "Evaluate Random Forest performance using the frozen base pair-level feature table.",
        "tools": "Python, pandas, scikit-learn RandomForestClassifier",
        "data": "outputs/features/pair_level_features_base_frozen.csv",
        "procedure": "A Random Forest with 300 trees, shallow max depth, minimum leaf size of 2, and balanced class weights was trained in each grouped fold. Each fold held out one complete dataset folder.",
        "analysis": "The model achieves perfect grouped-evaluation performance with base pair-level features, indicating that the original engineered variables already contain strong discriminative signal.",
    },
    {
        "id": "EXP-04",
        "title": "Random Forest with Contextual Features",
        "experiment": "random_forest_enhanced",
        "name": "Random Forest contextual-feature model",
        "objective": "Evaluate Random Forest performance after adding contextual ranks, z-scores, and sequence-derived features.",
        "tools": "Python, pandas, scikit-learn RandomForestClassifier",
        "data": "outputs/features/pair_level_features_enhanced.csv",
        "procedure": "The same Random Forest configuration was trained using the enhanced contextual feature table and the same grouped 5-fold split.",
        "analysis": "The contextual Random Forest also achieves perfect performance. Because the base model was already perfect, contextual features do not improve headline metrics but provide richer explanatory evidence.",
    },
    {
        "id": "EXP-05",
        "title": "Random Forest without Message-Length Features",
        "experiment": "random_forest_no_length",
        "name": "Random Forest no-length ablation",
        "objective": "Test whether Random Forest performance depends on message-length-derived features.",
        "tools": "Python, pandas, scikit-learn RandomForestClassifier",
        "data": "outputs/features/pair_level_features_enhanced.csv with length-derived columns removed",
        "procedure": "All message-length-related features were removed, leaving 36 numeric features. The Random Forest was retrained using the same grouped folds.",
        "analysis": "Performance drops compared with the full feature set. This shows that the Random Forest relies strongly on message-length signals and supports the synthetic-shortcut limitation discussion.",
    },
    {
        "id": "EXP-06",
        "title": "SVM with Base Features",
        "experiment": "svm_rbf_base",
        "name": "SVM base-feature model",
        "objective": "Evaluate an RBF-kernel SVM using the frozen base feature table.",
        "tools": "Python, pandas, scikit-learn SVC",
        "data": "outputs/features/pair_level_features_base_frozen.csv",
        "procedure": "A pipeline with median imputation, standard scaling, and class-balanced RBF SVM was trained in each grouped fold.",
        "analysis": "The SVM achieves perfect performance on base features, showing that the class boundary is separable with the original pair-level variables.",
    },
    {
        "id": "EXP-07",
        "title": "SVM with Contextual Features",
        "experiment": "svm_rbf_enhanced",
        "name": "SVM contextual-feature model",
        "objective": "Evaluate the RBF-kernel SVM with enhanced contextual features.",
        "tools": "Python, pandas, scikit-learn SVC",
        "data": "outputs/features/pair_level_features_enhanced.csv",
        "procedure": "The same SVM preprocessing and model setup was trained using the enhanced feature table under grouped 5-fold evaluation.",
        "analysis": "The contextual SVM achieves perfect performance. Together with the ablation result, this suggests the SVM can exploit both length and non-length contextual signals.",
    },
    {
        "id": "EXP-08",
        "title": "SVM without Message-Length Features",
        "experiment": "svm_rbf_no_length",
        "name": "SVM no-length ablation",
        "objective": "Test whether SVM performance remains robust when message-length-derived features are removed.",
        "tools": "Python, pandas, scikit-learn SVC",
        "data": "outputs/features/pair_level_features_enhanced.csv with length-derived columns removed",
        "procedure": "The no-length feature set was used with the same imputation, scaling, class weighting, and grouped folds as the full SVM model.",
        "analysis": "The SVM remains perfect without message-length features, suggesting that other contextual variables still separate the labelled pairs in PASYDA.",
    },
    {
        "id": "EXP-09",
        "title": "MLP with Base Features",
        "experiment": "mlp_small_base",
        "name": "Small MLP base-feature model",
        "objective": "Evaluate a lightweight deep learning model on the frozen base pair-level features.",
        "tools": "Python, pandas, scikit-learn MLPClassifier",
        "data": "outputs/features/pair_level_features_base_frozen.csv",
        "procedure": "A small MLP with 32 and 16 hidden units was trained with median imputation, standard scaling, and positive-class oversampling inside training folds only.",
        "analysis": "The MLP achieves perfect performance on base features. The result confirms that a lightweight tabular deep model is sufficient for this small engineered-feature dataset.",
    },
    {
        "id": "EXP-10",
        "title": "MLP with Contextual Features",
        "experiment": "mlp_small_enhanced",
        "name": "Small MLP contextual-feature model",
        "objective": "Evaluate the lightweight MLP using enhanced contextual and sequence-derived features.",
        "tools": "Python, pandas, scikit-learn MLPClassifier",
        "data": "outputs/features/pair_level_features_enhanced.csv",
        "procedure": "The same MLP architecture and fold-safe oversampling approach were used with the enhanced feature table.",
        "analysis": "The contextual MLP achieves perfect performance. However, this should be interpreted alongside the message-length baseline and ablation results.",
    },
    {
        "id": "EXP-11",
        "title": "MLP without Message-Length Features",
        "experiment": "mlp_small_no_length",
        "name": "Small MLP no-length ablation",
        "objective": "Test whether the MLP remains robust after removing message-length-derived features.",
        "tools": "Python, pandas, scikit-learn MLPClassifier",
        "data": "outputs/features/pair_level_features_enhanced.csv with length-derived columns removed",
        "procedure": "The MLP was retrained on the 36-feature no-length table using the same grouped folds and training-fold-only positive oversampling.",
        "analysis": "Performance drops slightly compared with the full feature set. This indicates some dependence on length-related signals, but the MLP still retains strong performance from other contextual features.",
    },
]


def metric_row(metrics: pd.DataFrame, experiment: str) -> pd.Series:
    rows = metrics[metrics["experiment"] == experiment]
    if rows.empty:
        raise ValueError(f"Missing metrics for experiment: {experiment}")
    return rows.iloc[0]


def metric_table(row: pd.Series) -> str:
    fields = [
        ("Top-1 Accuracy", "top1_accuracy_mean"),
        ("Mean Reciprocal Rank", "mean_reciprocal_rank_mean"),
        ("Precision at Top-1", "precision_at_top1_mean"),
        ("Recall at Top-1", "recall_at_top1_mean"),
        ("F1 at Top-1", "f1_at_top1_mean"),
        ("ROC-AUC", "roc_auc_mean"),
        ("PR-AUC", "pr_auc_mean"),
    ]
    lines = ["| Metric | Mean across folds |", "|---|---:|"]
    for label, column in fields:
        lines.append(f"| {label} | {float(row[column]):.4f} |")
    return "\n".join(lines)


def write_report(experiment: dict[str, str], row: pd.Series) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"{experiment['id']}_{experiment['experiment']}.md"
    content = f"""# {experiment['title']}

## Experiment No

{experiment['id']}

## Date

2026-06-09

## Name

{experiment['name']}

## Objective

{experiment['objective']}

## Tools Used

{experiment['tools']}

## Data Used

{experiment['data']}

## Procedure

{experiment['procedure']}

Grouped 5-fold evaluation was used. Each fold held out one complete dataset folder and evaluated on the two scenarios inside that folder. Folds were not treated as separate experiments; fold metrics were aggregated for this report.

## Results

{metric_table(row)}

Detailed fold-level results are available in `outputs/metrics/grouped_evaluation`.

## Analysis of Results

{experiment['analysis']}

The result should be interpreted with the broader portfolio findings: message-length features are unusually predictive in PASYDA, and false-positive/false-negative risks remain important even when aggregate metrics are high.
"""
    path.write_text(content, encoding="utf-8")


def write_index(metrics: pd.DataFrame) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Portfolio Experiment Index",
        "",
        "| Experiment No | Experiment | Top-1 | MRR | F1 | ROC-AUC | PR-AUC |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for experiment in EXPERIMENTS:
        row = metric_row(metrics, experiment["experiment"])
        lines.append(
            "| {id} | {title} | {top1:.4f} | {mrr:.4f} | {f1:.4f} | {roc:.4f} | {pr:.4f} |".format(
                id=experiment["id"],
                title=experiment["title"],
                top1=float(row["top1_accuracy_mean"]),
                mrr=float(row["mean_reciprocal_rank_mean"]),
                f1=float(row["f1_at_top1_mean"]),
                roc=float(row["roc_auc_mean"]),
                pr=float(row["pr_auc_mean"]),
            )
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Each report describes one experiment configuration.",
            "- The 5 grouped folds are internal evaluation repeats, not separate experiment reports.",
            "- Full-feature models achieve perfect performance, but no-length ablations are included to test synthetic shortcut risk.",
            "- False alerts and missed detections are discussed in `../error_and_false_alert_discussion.md`.",
        ]
    )
    (REPORT_DIR / "portfolio_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    baseline_metrics = pd.read_csv(METRICS_DIR / "baseline_metrics_summary.csv")
    model_metrics = pd.read_csv(METRICS_DIR / "model_metrics_summary.csv")
    metrics = pd.concat([baseline_metrics, model_metrics], ignore_index=True)

    for experiment in EXPERIMENTS:
        write_report(experiment, metric_row(metrics, experiment["experiment"]))
    write_index(metrics)

    print(f"Wrote {len(EXPERIMENTS)} experiment reports to {REPORT_DIR}")
    print(f"Wrote index to {REPORT_DIR / 'portfolio_index.md'}")


if __name__ == "__main__":
    main()
