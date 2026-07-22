from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import warnings

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.base import clone


warnings.filterwarnings(
    "ignore",
    message="The `probability` parameter was deprecated",
    category=FutureWarning,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_TABLE = PROJECT_ROOT / "outputs" / "features" / "pair_level_features_enhanced.csv"
BASE_FEATURE_TABLE = PROJECT_ROOT / "outputs" / "features" / "pair_level_features_base_frozen.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "metrics" / "grouped_evaluation"

ID_COLUMNS = {
    "folder",
    "scenario",
    "central_node",
    "contact_node",
    "pair_key",
    "label",
    "label_name",
    "first_message",
    "last_message",
}


@dataclass(frozen=True)
class Fold:
    fold_id: int
    test_folder: str
    train_folders: tuple[str, ...]


BASELINE_SCORES = {
    "baseline_highest_message_count": "message_count",
    "baseline_longest_duration": "duration_hours",
    "baseline_lowest_mean_length": "mean_length",
    "baseline_highest_evening_ratio": "evening_ratio",
    "baseline_highest_short_message_ratio": "short_message_ratio",
}

WEIGHTED_BASELINE_NAME = "baseline_weighted_contextual_heuristic"


LOWER_IS_BETTER = {
    "baseline_lowest_mean_length",
}

MODEL_DEFINITIONS = {
    "random_forest": {
        "needs_balanced_training": False,
        "estimator": RandomForestClassifier(
            n_estimators=300,
            max_depth=4,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
        ),
    },
    "svm_rbf": {
        "needs_balanced_training": False,
        "estimator": Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    SVC(
                        kernel="rbf",
                        C=1.0,
                        gamma="scale",
                        class_weight="balanced",
                        probability=False,
                        random_state=42,
                    ),
                ),
            ]
        ),
    },
    "mlp_small": {
        "needs_balanced_training": True,
        "estimator": Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    MLPClassifier(
                        hidden_layer_sizes=(32, 16),
                        activation="relu",
                        alpha=0.01,
                        learning_rate_init=0.001,
                        max_iter=2000,
                        random_state=42,
                        early_stopping=False,
                    ),
                ),
            ]
        ),
    },
}

LENGTH_ABLATION_PATTERNS = (
    "length",
    "short_message",
)


def load_feature_table(path: Path = FEATURE_TABLE) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"folder", "scenario", "label"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Feature table is missing required columns: {sorted(missing)}")
    return df


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    return [column for column in numeric_columns if column not in ID_COLUMNS]


def get_no_length_feature_columns(feature_columns: list[str]) -> list[str]:
    return [
        column
        for column in feature_columns
        if not any(pattern in column for pattern in LENGTH_ABLATION_PATTERNS)
    ]


def make_grouped_folds(df: pd.DataFrame) -> list[Fold]:
    folders = sorted(df["folder"].unique())
    folds = []
    for index, test_folder in enumerate(folders, start=1):
        train_folders = tuple(folder for folder in folders if folder != test_folder)
        folds.append(Fold(index, test_folder, train_folders))
    return folds


def validate_fold_data(train_df: pd.DataFrame, test_df: pd.DataFrame, fold: Fold) -> None:
    train_folders = set(train_df["folder"].unique())
    test_folders = set(test_df["folder"].unique())

    if train_folders.intersection(test_folders):
        raise ValueError(f"Folder leakage detected in fold {fold.fold_id}")
    if test_folders != {fold.test_folder}:
        raise ValueError(f"Unexpected test folders in fold {fold.fold_id}: {sorted(test_folders)}")
    if test_df.groupby("scenario")["label"].sum().ne(1).any():
        raise ValueError(f"Each test scenario must contain exactly one positive pair in fold {fold.fold_id}")


def scenario_ranks(predictions: pd.DataFrame) -> pd.DataFrame:
    ranked = predictions.copy()
    ranked["score_rank"] = ranked.groupby("scenario")["score"].rank(
        ascending=False,
        method="first",
    )
    return ranked


def binary_metrics_from_top1(ranked_predictions: pd.DataFrame) -> dict[str, float]:
    top1 = ranked_predictions[ranked_predictions["score_rank"] == 1].copy()
    true_positives = int(top1["label"].sum())
    false_positives = int((top1["label"] == 0).sum())
    total_positives = int(ranked_predictions["label"].sum())
    false_negatives = total_positives - true_positives

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return {
        "precision_at_top1": precision,
        "recall_at_top1": recall,
        "f1_at_top1": f1,
    }


def ranking_metrics(ranked_predictions: pd.DataFrame) -> dict[str, float]:
    positive_rows = ranked_predictions[ranked_predictions["label"] == 1]
    positive_ranks = positive_rows["score_rank"].astype(float)
    top1_accuracy = float((positive_ranks == 1).mean())
    mean_reciprocal_rank = float((1.0 / positive_ranks).mean())

    metrics = {
        "top1_accuracy": top1_accuracy,
        "mean_reciprocal_rank": mean_reciprocal_rank,
        "mean_positive_rank": float(positive_ranks.mean()),
    }
    metrics.update(binary_metrics_from_top1(ranked_predictions))

    try:
        metrics["roc_auc"] = float(roc_auc_score(ranked_predictions["label"], ranked_predictions["score"]))
    except ValueError:
        metrics["roc_auc"] = 0.0

    try:
        metrics["pr_auc"] = float(average_precision_score(ranked_predictions["label"], ranked_predictions["score"]))
    except ValueError:
        metrics["pr_auc"] = 0.0

    return metrics


def baseline_predictions(test_df: pd.DataFrame, experiment_name: str, score_column: str) -> pd.DataFrame:
    predictions = test_df[
        ["folder", "scenario", "central_node", "contact_node", "pair_key", "label"]
    ].copy()
    score = pd.to_numeric(test_df[score_column], errors="coerce").fillna(0.0)
    if experiment_name in LOWER_IS_BETTER:
        score = -score
    predictions["score"] = score
    predictions["experiment"] = experiment_name
    return scenario_ranks(predictions)


def weighted_baseline_predictions(test_df: pd.DataFrame) -> pd.DataFrame:
    predictions = test_df[
        ["folder", "scenario", "central_node", "contact_node", "pair_key", "label"]
    ].copy()

    score = (
        1.0 * pd.to_numeric(test_df["message_count_z_in_scenario"], errors="coerce").fillna(0.0)
        + 1.0 * pd.to_numeric(test_df["duration_hours_z_in_scenario"], errors="coerce").fillna(0.0)
        - 1.5 * pd.to_numeric(test_df["mean_length_z_in_scenario"], errors="coerce").fillna(0.0)
        + 1.0 * pd.to_numeric(test_df["evening_ratio_z_in_scenario"], errors="coerce").fillna(0.0)
        + 1.0 * pd.to_numeric(test_df["short_message_ratio_z_in_scenario"], errors="coerce").fillna(0.0)
        + 0.5 * pd.to_numeric(test_df["late_night_ratio_z_in_scenario"], errors="coerce").fillna(0.0)
    )

    predictions["score"] = score
    predictions["experiment"] = WEIGHTED_BASELINE_NAME
    return scenario_ranks(predictions)


def run_grouped_baselines(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    folds = make_grouped_folds(df)
    fold_rows = []
    prediction_tables = []
    metric_rows = []

    for fold in folds:
        train_df = df[df["folder"].isin(fold.train_folders)].copy()
        test_df = df[df["folder"] == fold.test_folder].copy()
        validate_fold_data(train_df, test_df, fold)

        fold_rows.append(
            {
                "fold_id": fold.fold_id,
                "test_folder": fold.test_folder,
                "train_folders": "|".join(fold.train_folders),
                "train_rows": len(train_df),
                "test_rows": len(test_df),
                "train_positives": int(train_df["label"].sum()),
                "test_positives": int(test_df["label"].sum()),
                "test_scenarios": test_df["scenario"].nunique(),
            }
        )

        for experiment_name, score_column in BASELINE_SCORES.items():
            ranked = baseline_predictions(test_df, experiment_name, score_column)
            ranked["fold_id"] = fold.fold_id
            ranked["test_folder"] = fold.test_folder
            prediction_tables.append(ranked)

            metrics = ranking_metrics(ranked)
            metric_rows.append(
                {
                    "experiment": experiment_name,
                    "fold_id": fold.fold_id,
                    "test_folder": fold.test_folder,
                    "test_scenarios": test_df["scenario"].nunique(),
                    **metrics,
                }
            )

        ranked = weighted_baseline_predictions(test_df)
        ranked["fold_id"] = fold.fold_id
        ranked["test_folder"] = fold.test_folder
        prediction_tables.append(ranked)

        metrics = ranking_metrics(ranked)
        metric_rows.append(
            {
                "experiment": WEIGHTED_BASELINE_NAME,
                "fold_id": fold.fold_id,
                "test_folder": fold.test_folder,
                "test_scenarios": test_df["scenario"].nunique(),
                **metrics,
            }
        )

    folds_df = pd.DataFrame(fold_rows)
    predictions_df = pd.concat(prediction_tables, ignore_index=True)
    fold_metrics_df = pd.DataFrame(metric_rows)
    return folds_df, predictions_df, fold_metrics_df


def balanced_training_data(train_df: pd.DataFrame) -> pd.DataFrame:
    positive_df = train_df[train_df["label"] == 1]
    negative_df = train_df[train_df["label"] == 0]

    if positive_df.empty or negative_df.empty:
        return train_df

    repeats = len(negative_df) // len(positive_df)
    remainder = len(negative_df) % len(positive_df)
    sampled_positive = pd.concat(
        [
            *([positive_df] * repeats),
            positive_df.sample(n=remainder, replace=False, random_state=42) if remainder else positive_df.iloc[0:0],
        ],
        ignore_index=True,
    )
    return (
        pd.concat([negative_df, sampled_positive], ignore_index=True)
        .sample(frac=1.0, random_state=42)
        .reset_index(drop=True)
    )


def model_scores(estimator: object, x_test: pd.DataFrame) -> pd.Series:
    if hasattr(estimator, "predict_proba"):
        return pd.Series(estimator.predict_proba(x_test)[:, 1], index=x_test.index)
    if hasattr(estimator, "decision_function"):
        return pd.Series(estimator.decision_function(x_test), index=x_test.index)
    return pd.Series(estimator.predict(x_test), index=x_test.index)


def train_model_predictions(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_columns: list[str],
    experiment_name: str,
    model_config: dict[str, object],
) -> pd.DataFrame:
    model_train_df = balanced_training_data(train_df) if model_config["needs_balanced_training"] else train_df

    x_train = model_train_df[feature_columns]
    y_train = model_train_df["label"].astype(int)
    x_test = test_df[feature_columns]

    estimator = clone(model_config["estimator"])
    estimator.fit(x_train, y_train)

    predictions = test_df[
        ["folder", "scenario", "central_node", "contact_node", "pair_key", "label"]
    ].copy()
    predictions["score"] = model_scores(estimator, x_test)
    predictions["experiment"] = experiment_name
    return scenario_ranks(predictions)


def run_grouped_models(
    df: pd.DataFrame,
    feature_columns: list[str],
    feature_set_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    folds = make_grouped_folds(df)
    prediction_tables = []
    metric_rows = []

    for fold in folds:
        train_df = df[df["folder"].isin(fold.train_folders)].copy()
        test_df = df[df["folder"] == fold.test_folder].copy()
        validate_fold_data(train_df, test_df, fold)

        for experiment_name, model_config in MODEL_DEFINITIONS.items():
            full_experiment_name = f"{experiment_name}_{feature_set_name}"
            ranked = train_model_predictions(
                train_df=train_df,
                test_df=test_df,
                feature_columns=feature_columns,
                experiment_name=full_experiment_name,
                model_config=model_config,
            )
            ranked["fold_id"] = fold.fold_id
            ranked["test_folder"] = fold.test_folder
            ranked["feature_set"] = feature_set_name
            prediction_tables.append(ranked)

            metrics = ranking_metrics(ranked)
            metric_rows.append(
                {
                    "experiment": full_experiment_name,
                    "model": experiment_name,
                    "feature_set": feature_set_name,
                    "fold_id": fold.fold_id,
                    "test_folder": fold.test_folder,
                    "test_scenarios": test_df["scenario"].nunique(),
                    **metrics,
                }
            )

    predictions_df = pd.concat(prediction_tables, ignore_index=True)
    fold_metrics_df = pd.DataFrame(metric_rows)
    return predictions_df, fold_metrics_df


def aggregate_metrics(fold_metrics_df: pd.DataFrame) -> pd.DataFrame:
    metric_columns = [
        "top1_accuracy",
        "mean_reciprocal_rank",
        "mean_positive_rank",
        "precision_at_top1",
        "recall_at_top1",
        "f1_at_top1",
        "roc_auc",
        "pr_auc",
    ]
    aggregate = (
        fold_metrics_df.groupby("experiment")[metric_columns]
        .agg(["mean", "std"])
        .round(4)
        .reset_index()
    )
    aggregate.columns = [
        column if isinstance(column, str) else "_".join(part for part in column if part)
        for column in aggregate.columns
    ]
    return aggregate


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_feature_table()
    base_df = load_feature_table(BASE_FEATURE_TABLE)
    feature_columns = get_feature_columns(df)
    base_feature_columns = get_feature_columns(base_df)
    no_length_feature_columns = get_no_length_feature_columns(feature_columns)
    folds_df, baseline_predictions_df, baseline_fold_metrics_df = run_grouped_baselines(df)
    baseline_aggregate_df = aggregate_metrics(baseline_fold_metrics_df)
    base_model_predictions_df, base_model_fold_metrics_df = run_grouped_models(
        base_df,
        base_feature_columns,
        "base",
    )
    full_model_predictions_df, full_model_fold_metrics_df = run_grouped_models(
        df,
        feature_columns,
        "enhanced",
    )
    no_length_model_predictions_df, no_length_model_fold_metrics_df = run_grouped_models(
        df,
        no_length_feature_columns,
        "no_length",
    )
    model_predictions_df = pd.concat(
        [base_model_predictions_df, full_model_predictions_df, no_length_model_predictions_df],
        ignore_index=True,
    )
    model_fold_metrics_df = pd.concat(
        [base_model_fold_metrics_df, full_model_fold_metrics_df, no_length_model_fold_metrics_df],
        ignore_index=True,
    )
    model_aggregate_df = aggregate_metrics(model_fold_metrics_df)
    all_fold_metrics_df = pd.concat([baseline_fold_metrics_df, model_fold_metrics_df], ignore_index=True)
    all_aggregate_df = aggregate_metrics(all_fold_metrics_df)

    feature_columns_df = pd.DataFrame({"feature": feature_columns})
    base_feature_columns_df = pd.DataFrame({"feature": base_feature_columns})
    no_length_feature_columns_df = pd.DataFrame({"feature": no_length_feature_columns})
    removed_feature_columns_df = pd.DataFrame(
        {
            "feature": [
                column for column in feature_columns if column not in no_length_feature_columns
            ]
        }
    )
    base_feature_columns_df.to_csv(OUTPUT_DIR / "feature_columns_base.csv", index=False)
    feature_columns_df.to_csv(OUTPUT_DIR / "feature_columns.csv", index=False)
    no_length_feature_columns_df.to_csv(OUTPUT_DIR / "feature_columns_no_length.csv", index=False)
    removed_feature_columns_df.to_csv(OUTPUT_DIR / "feature_columns_removed_for_no_length_ablation.csv", index=False)
    folds_df.to_csv(OUTPUT_DIR / "fold_assignments.csv", index=False)
    baseline_predictions_df.to_csv(OUTPUT_DIR / "baseline_predictions_by_fold.csv", index=False)
    baseline_fold_metrics_df.to_csv(OUTPUT_DIR / "baseline_fold_metrics.csv", index=False)
    baseline_aggregate_df.to_csv(OUTPUT_DIR / "baseline_metrics_summary.csv", index=False)
    model_predictions_df.to_csv(OUTPUT_DIR / "model_predictions_by_fold.csv", index=False)
    model_fold_metrics_df.to_csv(OUTPUT_DIR / "model_fold_metrics.csv", index=False)
    model_aggregate_df.to_csv(OUTPUT_DIR / "model_metrics_summary.csv", index=False)
    all_fold_metrics_df.to_csv(OUTPUT_DIR / "all_fold_metrics.csv", index=False)
    all_aggregate_df.to_csv(OUTPUT_DIR / "all_metrics_summary.csv", index=False)

    print(f"Feature table: {FEATURE_TABLE}")
    print(f"Output folder: {OUTPUT_DIR}")
    print(f"Rows: {len(df)}")
    print(f"Base feature columns: {len(base_feature_columns)}")
    print(f"Feature columns: {len(feature_columns)}")
    print(f"No-length feature columns: {len(no_length_feature_columns)}")
    print(f"Removed length-related columns: {len(removed_feature_columns_df)}")
    print(f"Folds: {len(folds_df)}")
    print("Fold assignments:")
    print(folds_df.to_string(index=False))
    print("\nBaseline metrics summary:")
    print(baseline_aggregate_df.to_string(index=False))
    print("\nModel metrics summary:")
    print(model_aggregate_df.to_string(index=False))


if __name__ == "__main__":
    main()
