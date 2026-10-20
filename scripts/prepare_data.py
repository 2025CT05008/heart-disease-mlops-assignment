"""Clean the supplied raw data and produce EDA visuals."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from heart_ml.data import FEATURE_COLUMNS, clean_heart_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data/raw/heart_disease_combined.csv"
CLEAN_PATH = ROOT / "data/cleaned/heart_disease_cleaned.csv"
FIGURES = ROOT / "reports/figures"


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    cleaned = clean_heart_data(pd.read_csv(RAW_PATH))
    cleaned.to_csv(CLEAN_PATH, index=False)
    sns.set_theme(style="whitegrid", context="notebook")

    ax = (
        cleaned["target"]
        .value_counts()
        .sort_index()
        .rename({0: "No disease", 1: "Disease"})
        .plot.bar(color=["#4C78A8", "#E45756"], figsize=(6, 4), rot=0)
    )
    ax.set(title="Class balance", xlabel="Target", ylabel="Patients")
    plt.tight_layout()
    plt.savefig(FIGURES / "class_balance.png", dpi=180)
    plt.close()

    cleaned[["age", "trestbps", "chol", "thalach", "oldpeak"]].hist(
        figsize=(10, 6), bins=20, color="#4C78A8"
    )
    plt.suptitle("Distribution of selected clinical variables", y=1.02)
    plt.tight_layout()
    plt.savefig(FIGURES / "feature_histograms.png", dpi=180, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(11, 9))
    sns.heatmap(cleaned[FEATURE_COLUMNS + ["target"]].corr(), cmap="vlag", center=0, square=True)
    plt.title("Feature correlation heatmap")
    plt.tight_layout()
    plt.savefig(FIGURES / "correlation_heatmap.png", dpi=180)
    plt.close()
    print(f"Wrote {len(cleaned)} cleaned rows to {CLEAN_PATH}")


if __name__ == "__main__":
    main()
