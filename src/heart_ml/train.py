"""Train, evaluate, track, and package the selected classifier."""

import argparse
import json
from pathlib import Path

import joblib
import mlflow
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split

from heart_ml.data import FEATURE_COLUMNS, TARGET_COLUMN, load_clean_data
from heart_ml.model import candidate_models


def evaluate(y_true, probabilities) -> dict[str, float]:
    predictions = (probabilities >= 0.5).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision": float(precision_score(y_true, predictions, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/cleaned/heart_disease_cleaned.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    root = Path.cwd()
    data = load_clean_data(root / args.data)
    x, y = data[FEATURE_COLUMNS], data[TARGET_COLUMN]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=args.seed, stratify=y
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=args.seed)
    mlflow.set_tracking_uri(f"file://{root / 'mlruns'}")
    mlflow.set_experiment("heart-disease-classification")
    results: dict[str, dict[str, float]] = {}
    fitted: dict[str, object] = {}
    for name, pipeline in candidate_models(args.seed).items():
        with mlflow.start_run(run_name=name):
            scores = cross_validate(
                pipeline,
                x_train,
                y_train,
                cv=cv,
                scoring=["accuracy", "precision", "recall", "roc_auc"],
                n_jobs=1,
            )
            pipeline.fit(x_train, y_train)
            metrics = evaluate(y_test, pipeline.predict_proba(x_test)[:, 1])
            metrics.update(
                {
                    f"cv_{key[5:]}_mean": float(np.mean(value))
                    for key, value in scores.items()
                    if key.startswith("test_")
                }
            )
            mlflow.log_params({"model": name, "seed": args.seed, "cv_folds": 5})
            mlflow.log_metrics(metrics)
            results[name] = metrics
            fitted[name] = pipeline
    selected_name = max(results, key=lambda name: results[name]["roc_auc"])
    selected_model = fitted[selected_name]
    model_dir, report_dir = root / "models", root / "reports"
    figure_dir = report_dir / "figures"
    model_dir.mkdir(exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(selected_model, model_dir / "heart_disease_pipeline.joblib")
    metadata = {
        "selected_model": selected_name,
        "holdout_metrics": results[selected_name],
        "features": FEATURE_COLUMNS,
    }
    (model_dir / "model_metadata.json").write_text(json.dumps(metadata, indent=2))
    (report_dir / "metrics.json").write_text(json.dumps(results, indent=2))

    # Import plotting only after durable model and metrics artifacts exist. This keeps
    # training usable in lean CI containers where Matplotlib's font cache is slow.
    import matplotlib.pyplot as plt
    import seaborn as sns

    probabilities = selected_model.predict_proba(x_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    sns.heatmap(
        confusion_matrix(y_test, predictions), annot=True, fmt="d", cmap="Blues", ax=axes[0]
    )
    axes[0].set(title=f"Confusion matrix: {selected_name}", xlabel="Predicted", ylabel="Actual")
    fpr, tpr, _ = roc_curve(y_test, probabilities)
    axes[1].plot(fpr, tpr, label=f"AUC = {results[selected_name]['roc_auc']:.3f}")
    axes[1].plot([0, 1], [0, 1], "--", color="gray")
    axes[1].set(title="ROC curve", xlabel="False positive rate", ylabel="True positive rate")
    axes[1].legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(figure_dir / "model_evaluation.png", dpi=180)
    plt.close(fig)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
