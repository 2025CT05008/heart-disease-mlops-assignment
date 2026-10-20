import pandas as pd

from heart_ml.data import FEATURE_COLUMNS
from heart_ml.model import candidate_models


def test_candidates_fit_and_predict_probability() -> None:
    x = pd.DataFrame(
        [{feature: i + row for i, feature in enumerate(FEATURE_COLUMNS)} for row in range(12)]
    )
    x["sex"] = x["sex"] % 2
    x["fbs"] = x["fbs"] % 2
    x["exang"] = x["exang"] % 2
    x["cp"] = (x["cp"] % 4) + 1
    x["restecg"] = x["restecg"] % 3
    x["slope"] = (x["slope"] % 3) + 1
    x["thal"] = 3
    y = [0, 1] * 6
    model = candidate_models()["logistic_regression"].fit(x, y)
    assert model.predict_proba(x).shape == (12, 2)
