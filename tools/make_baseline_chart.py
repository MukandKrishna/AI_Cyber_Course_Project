import csv
from pathlib import Path

import matplotlib.pyplot as plt


INPUT = Path("outputs/metrics/grouped_evaluation/baseline_metrics_summary.csv")
OUTPUT = Path("outputs/metrics/grouped_evaluation/baseline_top1_accuracy.png")

LABELS = {
    "baseline_highest_message_count": "Highest message\ncount",
    "baseline_longest_duration": "Longest\nduration",
    "baseline_lowest_mean_length": "Lowest mean\nlength",
    "baseline_highest_evening_ratio": "Highest evening\nratio",
    "baseline_highest_short_message_ratio": "Highest short-message\nratio",
    "baseline_weighted_contextual_heuristic": "Weighted contextual\nheuristic",
}


def main():
    rows = []
    with INPUT.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["experiment"]
            if name in LABELS:
                rows.append((LABELS[name], float(row["top1_accuracy_mean"])))

    plt.figure(figsize=(9, 4.8))
    bars = plt.bar([r[0] for r in rows], [r[1] for r in rows], color="#4C78A8")
    plt.ylim(0, 1.08)
    plt.ylabel("Top-1 Accuracy")
    plt.title("Top-1 Accuracy of Heuristic Baselines")
    plt.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=0, ha="center")

    for bar, (_, value) in zip(bars, rows):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.025,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT, dpi=200)
    print(OUTPUT)


if __name__ == "__main__":
    main()
