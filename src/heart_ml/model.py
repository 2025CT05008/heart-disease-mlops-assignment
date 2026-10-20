"""Pipeline construction helpers."""

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from heart_ml.data import FEATURE_COLUMNS


def build_preprocessor() -> ColumnTransformer:
    numeric_steps = Pipeline(
        [("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
    )
    return ColumnTransformer([("numeric", numeric_steps, FEATURE_COLUMNS)], remainder="drop")


def candidate_models(random_state: int = 42) -> dict[str, Pipeline]:
    preprocessor = build_preprocessor()
    return {
        "logistic_regression": Pipeline(
            [("preprocessor", preprocessor), ("classifier", LogisticRegression(max_iter=2000))]
        ),
        "random_forest": Pipeline(
            [
                ("preprocessor", preprocessor),
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=300,
                        min_samples_leaf=2,
                        class_weight="balanced",
                        random_state=random_state,
                        n_jobs=1,
                    ),
                ),
            ]
        ),
    }
