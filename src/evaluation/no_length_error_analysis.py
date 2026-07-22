from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
METRICS_DIR = PROJECT_ROOT / "outputs" / "metrics" / "grouped_evaluation"
OUT_PATH = METRICS_DIR / "no_length_error_cases.csv"
SUMMARY_PATH = METRICS_DIR / "no_length_error_summary.csv"


def main() -> None:
    predictions = pd.read_csv(METRICS_DIR / "model_predictions_by_fold.csv")
    no_length = predictions[predictions["feature_set"] == "no_length"].copy()
    positives = no_length[no_length["label"] == 1].copy()
    errors = positives[positives["score_rank"] != 1].copy()
    errors = errors[
        [
            "experiment",
            "fold_id",
            "test_folder",
            "scenario",
            "central_node",
            "contact_node",
            "pair_key",
            "score",
            "score_rank",
        ]
    ].sort_values(["experiment", "fold_id", "scenario"])

    summary = (
        positives.assign(error=positives["score_rank"].ne(1))
        .groupby("experiment", as_index=False)
        .agg(
            true_pairs=("label", "count"),
            missed_top1=("error", "sum"),
            worst_true_rank=("score_rank", "max"),
            mean_true_rank=("score_rank", "mean"),
        )
    )

    errors.to_csv(OUT_PATH, index=False)
    summary.to_csv(SUMMARY_PATH, index=False)
    print(f"Wrote {OUT_PATH}")
    print(f"Wrote {SUMMARY_PATH}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
