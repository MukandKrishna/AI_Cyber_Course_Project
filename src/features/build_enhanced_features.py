from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASE_FEATURES = PROJECT_ROOT / "outputs" / "features" / "pair_level_features_base_frozen.csv"
DATASET_ROOT = PROJECT_ROOT / "PASYDA" / "Dataset"
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "features" / "pair_level_features_enhanced.csv"

SHORT_MESSAGE_LENGTH = 20
LATE_NIGHT_START_HOUR = 0
LATE_NIGHT_END_HOUR = 5


def pair_key(node_a: object, node_b: object) -> str:
    return "|".join(sorted([str(node_a), str(node_b)]))


def safe_ratio(numerator: float, denominator: float) -> float:
    return float(numerator) / float(denominator) if denominator else 0.0


def load_vic_data(folder: str, scenario: str) -> pd.DataFrame:
    path = DATASET_ROOT / folder / f"{scenario}_vic_data.csv"
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Length"] = pd.to_numeric(df["Length"], errors="coerce").fillna(0)
    df["pair_key"] = [pair_key(src, dst) for src, dst in zip(df["Source"], df["Destination"])]
    return df.sort_values("Date").reset_index(drop=True)


def direction_switch_frequency(pair_df: pd.DataFrame, central_node: str) -> float:
    if len(pair_df) <= 1:
        return 0.0

    directions = pair_df["Source"].astype(str).eq(str(central_node)).astype(int)
    switches = directions.ne(directions.shift()).iloc[1:].sum()
    return safe_ratio(float(switches), float(len(pair_df) - 1))


def sequence_features(row: pd.Series, scenario_cache: dict[tuple[str, str], pd.DataFrame]) -> dict[str, float]:
    cache_key = (row["folder"], row["scenario"])
    if cache_key not in scenario_cache:
        scenario_cache[cache_key] = load_vic_data(*cache_key)

    scenario_df = scenario_cache[cache_key]
    pair_df = scenario_df[scenario_df["pair_key"] == row["pair_key"]].copy()

    if pair_df.empty:
        return {
            "short_message_ratio": 0.0,
            "late_night_ratio": 0.0,
            "first_day_intensity": 0.0,
            "last_day_intensity": 0.0,
            "direction_switch_frequency": 0.0,
        }

    pair_df["message_day"] = pair_df["Date"].dt.date
    first_day = pair_df["message_day"].min()
    last_day = pair_df["message_day"].max()
    message_count = len(pair_df)

    late_night_mask = pair_df["Date"].dt.hour.between(
        LATE_NIGHT_START_HOUR,
        LATE_NIGHT_END_HOUR,
        inclusive="both",
    )

    return {
        "short_message_ratio": safe_ratio((pair_df["Length"] <= SHORT_MESSAGE_LENGTH).sum(), message_count),
        "late_night_ratio": safe_ratio(late_night_mask.sum(), message_count),
        "first_day_intensity": safe_ratio((pair_df["message_day"] == first_day).sum(), message_count),
        "last_day_intensity": safe_ratio((pair_df["message_day"] == last_day).sum(), message_count),
        "direction_switch_frequency": direction_switch_frequency(pair_df, str(row["central_node"])),
    }


def add_rank_features(df: pd.DataFrame) -> pd.DataFrame:
    ranked = df.copy()
    rank_specs = {
        "message_count": False,
        "duration_hours": False,
        "mean_length": True,
        "evening_ratio": False,
        "late_night_ratio": False,
        "short_message_ratio": False,
    }

    for column, ascending in rank_specs.items():
        ranked[f"{column}_rank_in_scenario"] = ranked.groupby("scenario")[column].rank(
            ascending=ascending,
            method="min",
        )
        ranked[f"{column}_pct_rank_in_scenario"] = ranked.groupby("scenario")[column].rank(
            ascending=ascending,
            pct=True,
            method="average",
        )

    return ranked


def add_zscore_features(df: pd.DataFrame) -> pd.DataFrame:
    zscored = df.copy()
    zscore_columns = [
        "message_count",
        "duration_hours",
        "mean_length",
        "median_length",
        "reciprocity_ratio",
        "evening_ratio",
        "night_ratio",
        "late_night_ratio",
        "short_message_ratio",
        "direction_switch_frequency",
        "message_share_in_scenario",
    ]

    for column in zscore_columns:
        group = zscored.groupby("scenario")[column]
        mean = group.transform("mean")
        std = group.transform("std").replace(0, pd.NA)
        zscored[f"{column}_z_in_scenario"] = ((zscored[column] - mean) / std).fillna(0.0)

    return zscored


def build_enhanced_features() -> pd.DataFrame:
    df = pd.read_csv(BASE_FEATURES)

    scenario_cache: dict[tuple[str, str], pd.DataFrame] = {}
    extra_rows = [sequence_features(row, scenario_cache) for _, row in df.iterrows()]
    extra_df = pd.DataFrame(extra_rows)

    enhanced = pd.concat([df.reset_index(drop=True), extra_df], axis=1)
    enhanced = add_rank_features(enhanced)
    enhanced = add_zscore_features(enhanced)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    enhanced.to_csv(OUTPUT_PATH, index=False)
    return enhanced


if __name__ == "__main__":
    features = build_enhanced_features()
    added_columns = [
        column
        for column in features.columns
        if column not in pd.read_csv(BASE_FEATURES, nrows=0).columns
    ]
    print(f"Wrote: {OUTPUT_PATH}")
    print(f"Rows: {len(features)}")
    print(f"Columns: {len(features.columns)}")
    print("Added columns:")
    for column in added_columns:
        print(f"- {column}")
