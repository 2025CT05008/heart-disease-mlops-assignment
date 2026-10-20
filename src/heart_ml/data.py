"""Dataset loading and cleaning utilities."""

from pathlib import Path

import pandas as pd

FEATURE_COLUMNS = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
]
TARGET_COLUMN = "target"


def clean_heart_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Return model-ready data with a binary target and no provenance feature.

    Original UCI `num` is 0-4. Values above zero represent heart-disease presence.
    Feature NaNs remain for the pipeline's within-fold median imputation, avoiding leakage.
    """
    required = set(FEATURE_COLUMNS + ["num"])
    absent = required - set(raw.columns)
    if absent:
        raise ValueError(f"Dataset is missing required columns: {sorted(absent)}")
    data = raw.copy().replace("?", pd.NA)
    for column in FEATURE_COLUMNS + ["num"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.dropna(subset=["num"])
    cleaned = data[FEATURE_COLUMNS].copy()
    cleaned[TARGET_COLUMN] = (data["num"] > 0).astype(int)
    return cleaned.reset_index(drop=True)


def load_clean_data(path: str | Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    required = set(FEATURE_COLUMNS + [TARGET_COLUMN])
    absent = required - set(data.columns)
    if absent:
        raise ValueError(f"Cleaned dataset is missing columns: {sorted(absent)}")
    return data
