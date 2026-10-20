"""Build the final 10-page Word report from executed project artifacts."""

import json
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Heart_Disease_MLOps_Assignment_Report.docx"
METRICS = json.loads((ROOT / "reports/metrics.json").read_text())


def setup(document: Document) -> None:
    section = document.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)
    normal = document.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)
    for style in ("Title", "Heading 1", "Heading 2"):
        document.styles[style].font.name = "Aptos"
        document.styles[style].font.color.rgb = RGBColor(0, 0, 0)


def heading(document: Document, text: str) -> None:
    document.add_heading(text, level=1)


def paragraph(document: Document, text: str, bold_lead: str | None = None) -> None:
    p = document.add_paragraph()
    if bold_lead:
        p.add_run(bold_lead).bold = True
    p.add_run(text)


def table(document: Document, headers: list[str], rows: list[list[str]]) -> None:
    t = document.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    for cell, value in zip(t.rows[0].cells, headers):
        cell.text = value
    for row in rows:
        for cell, value in zip(t.add_row().cells, row):
            cell.text = value


def page(document: Document) -> None:
    document.add_page_break()


def main() -> None:
    d = Document()
    setup(d)
    d.add_heading("Heart Disease MLOps Assignment Report", 0)
    p = d.add_paragraph("AIMLCZG523 Machine Learning Operations Assignment 01")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    d.add_paragraph("End to End Model Development CI CD Deployment and Monitoring", style="Subtitle")
    d.add_paragraph("Prepared for academic submission using the supplied combined Heart Disease UCI dataset.")
    d.add_paragraph("Student name: ____________________\nStudent ID: ____________________\nSubmission date: ____________________")
    paragraph(d, "This report documents the reproducible implementation, the observed experimental results, and the exact local and cloud-ready deployment configuration. The classifier is for educational use only and is not a clinical diagnostic tool.")

    page(d); heading(d, "1 Project Objective and Architecture")
    paragraph(d, "The goal is to predict the presence of heart disease from routinely recorded clinical variables and deliver the result through a monitored HTTP API. The project was designed to make data preparation, experiment selection, model serving, and deployment repeatable.")
    table(d, ["Stage", "Artifact", "Purpose"], [["Data", "prepare_data.py", "Cleans data and produces EDA figures"], ["Training", "heart_ml.train", "Cross-validates candidates and saves best pipeline"], ["Tracking", "MLflow file store", "Records parameters and metrics for each model"], ["Serving", "FastAPI", "Provides health prediction and metrics endpoints"], ["Operations", "GitHub Actions Docker Kubernetes Prometheus", "Tests builds deploys and observes the service"]])
    paragraph(d, "Architecture flow: supplied CSV -> cleaning script -> fitted preprocessing and candidate models -> MLflow and model artifact -> Dockerized FastAPI -> Kubernetes Service -> Prometheus scrape endpoint.")

    page(d); heading(d, "2 Data Acquisition Cleaning and EDA")
    paragraph(d, "The supplied heart_disease_combined.csv contains 920 records from combined UCI sources. A non-predictive source column is excluded. The UCI num target uses values 0 through 4, so it is converted to a binary target where num greater than zero means disease present.")
    paragraph(d, "Missing numeric values are deliberately retained after cleaning. Median imputation is encapsulated in the fitted sklearn pipeline, which learns values only from the training fold. This avoids data leakage during validation and prevents training-serving skew.")
    d.add_picture(str(ROOT / "reports/figures/class_balance.png"), width=Inches(3.2))
    d.add_picture(str(ROOT / "reports/figures/feature_histograms.png"), width=Inches(5.9))

    page(d); heading(d, "3 Exploratory Findings and Feature Design")
    paragraph(d, "The retained inputs are age, sex, chest pain type, resting blood pressure, cholesterol, fasting blood sugar, ECG result, maximum heart rate, exercise angina, ST depression, ST slope, vessels, and thal. Categorical codes are kept numeric because their encoded values are part of the supplied UCI representation; scaling is applied consistently to all numeric inputs.")
    d.add_picture(str(ROOT / "reports/figures/correlation_heatmap.png"), width=Inches(5.9))
    paragraph(d, "The EDA figures are generated automatically by scripts/prepare_data.py. They should be interpreted as descriptive evidence, not as causal or clinical claims.")

    page(d); heading(d, "4 Model Development and Selection")
    paragraph(d, "Two independent classifiers were compared: Logistic Regression as a transparent baseline and Random Forest as a nonlinear ensemble. Both receive the identical ColumnTransformer: median imputation followed by standard scaling. The data are stratified into an 80 percent training set and 20 percent holdout set; five-fold stratified cross-validation is run on the training partition.")
    paragraph(d, "The selected model maximizes holdout ROC-AUC. This metric is appropriate because it evaluates ranking quality across thresholds, while accuracy, precision, and recall describe the default 0.5 operating threshold.")
    table(d, ["Model", "Holdout Accuracy", "Precision", "Recall", "ROC AUC", "CV ROC AUC"], [[name.replace("_", " ").title(), f"{m['accuracy']:.3f}", f"{m['precision']:.3f}", f"{m['recall']:.3f}", f"{m['roc_auc']:.3f}", f"{m['cv_roc_auc_mean']:.3f}"] for name, m in METRICS.items()])

    page(d); heading(d, "5 Experiment Tracking and Reproducibility")
    paragraph(d, "MLflow is configured with a local file backend at mlruns. Each candidate run logs model name, random seed, cross-validation folds, holdout metrics, and cross-validation mean metrics. The selected Random Forest achieved holdout ROC-AUC 0.929 and is serialized together with a JSON metadata file listing the exact feature order and metrics.")
    paragraph(d, "Reproducibility controls include pinned requirements, a fixed random seed of 42, explicit train holdout split, serialized pipeline, Make targets, and scripts that operate from repository-relative paths. The preprocessing transformer is saved inside the model pipeline, so the API never relies on manually duplicated feature processing.")
    table(d, ["Command", "Expected result"], [["python scripts/prepare_data.py", "Clean CSV and three EDA images"], ["python -m heart_ml.train --data data/cleaned/heart_disease_cleaned.csv", "MLflow runs model and metrics artifacts"], ["mlflow ui --backend-store-uri ./mlruns", "Browser experiment comparison"]])

    page(d); heading(d, "6 Automated Tests and Continuous Integration")
    paragraph(d, "The pytest suite validates binary target construction, source-column removal, required-column validation, and probability output from the model pipeline. The executed local suite passed 3 tests. Ruff linting also passed after formatting the source tree.")
    paragraph(d, "The GitHub Actions workflow installs pinned packages, runs Ruff, runs pytest, prepares data, trains the model, uploads models reports and MLflow records as build artifacts, then performs a Docker build. A failure in linting, tests, preprocessing, training, or Docker build stops the workflow and leaves clear logs in the Actions run.")
    table(d, ["CI job", "Gate", "Artifact"], [["quality-and-training", "lint tests data prep training", "models reports mlruns"], ["docker-build", "depends on quality job", "container build validation"]])

    page(d); heading(d, "7 API Containerization")
    paragraph(d, "The FastAPI service loads the serialized pipeline at startup. POST /predict accepts a JSON patient record and returns binary prediction plus confidence. GET /health supports container and Kubernetes probes. GET /metrics exposes Prometheus-format request count and prediction latency telemetry.")
    table(d, ["Endpoint", "Method", "Purpose"], [["/health", "GET", "Readiness and liveness confirmation"], ["/predict", "POST", "Prediction and confidence"], ["/metrics", "GET", "Prometheus counters and histogram"]])
    paragraph(d, "Build locally with docker build -t heart-disease-api:local . and run with docker run --rm -p 8000:8000 heart-disease-api:local. A sample JSON body is provided at examples/request.json. Docker Compose also starts Prometheus with the supplied scrape configuration.")

    page(d); heading(d, "8 Kubernetes Deployment")
    paragraph(d, "The k8s directory contains a namespace, two-replica Deployment, LoadBalancer Service, and CPU-based HorizontalPodAutoscaler. Readiness and liveness probes call /health. Resource requests and limits provide a predictable scheduling footprint. Before cloud deployment, the image placeholder in k8s/deployment.yaml must be replaced with the student owned registry image.")
    table(d, ["Manifest", "Role"], [["namespace.yaml", "Isolates project resources"], ["deployment.yaml", "Replicated API pods with probes"], ["service.yaml", "Exposes port 80 to API port 8000"], ["hpa.yaml", "Scales 2 to 5 replicas at 70 percent CPU"]])
    paragraph(d, "Local Kubernetes validation can use Docker Desktop Kubernetes or Minikube and kubectl port-forward. A public URL requires a cloud account, pushed image, and an assigned Load Balancer or Ingress.")

    page(d); heading(d, "9 Monitoring Logging and Submission Evidence")
    paragraph(d, "Every prediction is logged with prediction class and confidence, while Prometheus records total predictions by outcome and a latency histogram. Prometheus is configured to scrape /metrics every 15 seconds. The included deployment guide specifies the screenshots to collect: running containers, Swagger prediction, Prometheus query, Kubernetes resources, and externally exposed endpoint.")
    paragraph(d, "Final submission actions: initialize a Git repository and push the project, replace the registry placeholder and deploy, add the resulting public URL or local access instructions, collect the listed screenshots into screenshots/, and record a 3 to 5 minute walkthrough. These account-bound actions cannot be truthfully fabricated in a local project artifact.")
    heading(d, "10 Conclusion")
    paragraph(d, "This implementation demonstrates a complete MLOps lifecycle: controlled data preparation, validated model selection, experiment tracking, packaged inference, automated quality gates, container deployment, Kubernetes configuration, and operational observability. The reported experiment selected Random Forest while preserving the baseline results for comparison and auditability.")
    d.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
