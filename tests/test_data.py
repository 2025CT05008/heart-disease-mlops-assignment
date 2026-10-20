import pandas as pd
import pytest

from heart_ml.data import FEATURE_COLUMNS, clean_heart_data


def test_cleaning_creates_binary_target_and_drops_source() -> None:
    frame = pd.DataFrame(
        [
            {**{col: 1 for col in FEATURE_COLUMNS}, "num": 0, "source": "a"},
            {**{col: 2 for col in FEATURE_COLUMNS}, "num": 3, "source": "b"},
        ]
    )
    cleaned = clean_heart_data(frame)
    assert cleaned["target"].tolist() == [0, 1]
    assert "source" not in cleaned.columns


def test_cleaning_rejects_missing_required_columns() -> None:
    with pytest.raises(ValueError, match="missing required"):
        clean_heart_data(pd.DataFrame({"num": [0]}))
