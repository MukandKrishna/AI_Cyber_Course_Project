from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from grouped_evaluation_pipeline import (
    FEATURE_TABLE,
    OUTPUT_DIR,
    balanced_training_data,
    get_feature_columns,
    load_feature_table,
    make_grouped_folds,
    ranking_metrics,
    scenario_ranks,
    train_model_predictions,
    validate_fold_data,
)


@dataclass(frozen=True)
class Candidate:
    model: str
    candidate_id: str
    estimator: object
    needs_balanced_training: bool


def candidates() -> list[Candidate]:
    return [
        Candidate(
            "random_forest",
            "rf_depth3_leaf2",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=3,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=42,
            ),
            False,
        ),
        Candidate(
            "random_forest",
            "rf_depth4_leaf2",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=4,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=42,
            ),
            False,
        ),
        Candidate(
            "random_forest",
            "rf_depthNone_leaf1",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=None,
                min_samples_leaf=1,
                class_weight="balanced",
                random_state=42,
            ),
            False,
        ),
        Candidate(
            "svm_rbf",
            "svm_C0.1",
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    ("classifier", SVC(kernel="rbf", C=0.1, gamma="scale", class_weight="balanced")),
                ]
            ),
            False,
        ),
        Candidate(
            "svm_rbf",
            "svm_C1",
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    ("classifier", SVC(kernel="rbf", C=1.0, gamma="scale", class_weight="balanced")),
                ]
            ),
            False,
        ),
        Candidate(
            "svm_rbf",
            "svm_C10",
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    ("classifier", SVC(kernel="rbf", C=10.0, gamma="scale", class_weight="balanced")),
                ]
            ),
            False,
        ),
        Candidate(
            "mlp_small",
            "mlp_16_alpha0.01",
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    (
                        "classifier",
                        MLPClassifier(
                            hidden_layer_sizes=(16,),
                            alpha=0.01,
                            max_iter=2000,
                            random_state=42,
                        ),
                    ),
                ]
            ),
            True,
        ),
        Candidate(
            "mlp_small",
            "mlp_32_16_alpha0.01",
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    (
                        "classifier",
                        MLPClassifier(
                            hidden_layer_sizes=(32, 16),
                            alpha=0.01,
                            max_iter=2000,
                            random_state=42,
                        ),
                    ),
                ]
            ),
            True,
        ),
        Candidate(
            "mlp_small",
            "mlp_32_16_alpha0.001",
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    (
                        "classifier",
                        MLPClassifier(
                            hidden_layer_sizes=(32, 16),
                            alpha=0.001,
                            max_iter=2000,
                            random_state=42,
                        ),
                    ),
                ]
            ),
            True,
        ),
    ]


def score_candidate(train_df: pd.DataFrame, valid_df: pd.DataFrame, feature_columns: list[str], candidate: Candidate) -> dict[str, float]:
    config = {
        "estimator": clone(candidate.estimator),
        "needs_balanced_training": candidate.needs_balanced_training,
    }
    ranked = train_model_predictions(
        train_df=train_df,
        test_df=valid_df,
        feature_columns=feature_columns,
        experiment_name=candidate.candidate_id,
        model_config=config,
    )
    return ranking_metrics(ranked)


def inner_group_scores(outer_train_df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    rows = []
    for candidate in candidates():
        for inner_fold in make_grouped_folds(outer_train_df):
            train_df = outer_train_df[outer_train_df["folder"].isin(inner_fold.train_folders)].copy()
            valid_df = outer_train_df[outer_train_df["folder"] == inner_fold.test_folder].copy()
            validate_fold_data(train_df, valid_df, inner_fold)
            metrics = score_candidate(train_df, valid_df, feature_columns, candidate)
            rows.append(
                {
                    "model": candidate.model,
                    "candidate_id": candidate.candidate_id,
                    "inner_valid_folder": inner_fold.test_folder,
                    **metrics,
                }
            )
    return pd.DataFrame(rows)


def choose_best(inner_scores: pd.DataFrame) -> pd.DataFrame:
    summary = (
        inner_scores.groupby(["model", "candidate_id"], as_index=False)
        .agg(
            inner_top1_mean=("top1_accuracy", "mean"),
            inner_mrr_mean=("mean_reciprocal_rank", "mean"),
            inner_pr_auc_mean=("pr_auc", "mean"),
        )
        .sort_values(
            ["model", "inner_top1_mean", "inner_mrr_mean", "inner_pr_auc_mean"],
            ascending=[True, False, False, False],
        )
    )
    return summary.groupby("model", as_index=False).first()


def run_nested_tuning() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = load_feature_table(FEATURE_TABLE)
    feature_columns = get_feature_columns(df)
    outer_rows = []
    inner_rows = []
    test_metric_rows = []
    candidate_lookup = {(c.model, c.candidate_id): c for c in candidates()}

    for outer_fold in make_grouped_folds(df):
        outer_train = df[df["folder"].isin(outer_fold.train_folders)].copy()
        outer_test = df[df["folder"] == outer_fold.test_folder].copy()
        validate_fold_data(outer_train, outer_test, outer_fold)

        inner_scores = inner_group_scores(outer_train, feature_columns)
        inner_scores["outer_fold_id"] = outer_fold.fold_id
        inner_scores["outer_test_folder"] = outer_fold.test_folder
        inner_rows.append(inner_scores)

        best = choose_best(inner_scores)
        best["outer_fold_id"] = outer_fold.fold_id
        best["outer_test_folder"] = outer_fold.test_folder
        outer_rows.append(best)

        for _, row in best.iterrows():
            candidate = candidate_lookup[(row["model"], row["candidate_id"])]
            ranked = train_model_predictions(
                train_df=outer_train,
                test_df=outer_test,
                feature_columns=feature_columns,
                experiment_name=f"{row['model']}_tuned",
                model_config={
                    "estimator": clone(candidate.estimator),
                    "needs_balanced_training": candidate.needs_balanced_training,
                },
            )
            metrics = ranking_metrics(ranked)
            test_metric_rows.append(
                {
                    "model": row["model"],
                    "selected_candidate": row["candidate_id"],
                    "outer_fold_id": outer_fold.fold_id,
                    "outer_test_folder": outer_fold.test_folder,
                    **metrics,
                }
            )

    return (
        pd.concat(inner_rows, ignore_index=True),
        pd.concat(outer_rows, ignore_index=True),
        pd.DataFrame(test_metric_rows),
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    inner_scores, selected, test_metrics = run_nested_tuning()
    summary = (
        test_metrics.groupby("model", as_index=False)
        .agg(
            top1_accuracy_mean=("top1_accuracy", "mean"),
            top1_accuracy_std=("top1_accuracy", "std"),
            mean_reciprocal_rank_mean=("mean_reciprocal_rank", "mean"),
            mean_reciprocal_rank_std=("mean_reciprocal_rank", "std"),
            f1_at_top1_mean=("f1_at_top1", "mean"),
            roc_auc_mean=("roc_auc", "mean"),
            pr_auc_mean=("pr_auc", "mean"),
        )
        .round(4)
    )
    inner_scores.to_csv(OUTPUT_DIR / "tuning_inner_scores.csv", index=False)
    selected.to_csv(OUTPUT_DIR / "tuning_selected_configs_by_outer_fold.csv", index=False)
    test_metrics.to_csv(OUTPUT_DIR / "tuning_outer_test_metrics.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "tuning_summary.csv", index=False)
    print("Nested tuning/sensitivity outputs written to:", OUTPUT_DIR)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
