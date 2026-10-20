# Heart Disease MLOps Classifier

An end-to-end, reproducible MLOps project for binary heart-disease risk classification using the supplied combined UCI Heart Disease data. The project compares Logistic Regression and Random Forest models, tracks experiments in MLflow, exposes the selected pipeline through FastAPI, and includes CI, Docker, Kubernetes, and Prometheus configuration.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python scripts/prepare_data.py
python -m heart_ml.train --data data/cleaned/heart_disease_cleaned.csv
uvicorn heart_ml.api:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/docs` for the interactive API. Run `mlflow ui --backend-store-uri ./mlruns` in another terminal to inspect runs.

## Local validation

```bash
pytest -q
ruff check src tests scripts
docker build -t heart-disease-api:local .
docker run --rm -p 8000:8000 heart-disease-api:local
curl -X POST http://localhost:8000/predict -H 'Content-Type: application/json' -d @examples/request.json
```

The service exposes `GET /health`, `GET /metrics`, and `POST /predict`.

## Container and Kubernetes deployment

```bash
docker compose up --build
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl -n heart-ml port-forward service/heart-disease-api 8000:80
```

For a public cloud deployment, replace the image in `k8s/deployment.yaml` with an image pushed to Docker Hub, GHCR, or the cloud registry, then configure an Ingress or cloud load balancer. See `docs/deployment-and-demo.md` for exact verification and screenshot/video checklist.

## Project structure

```text
data/               Raw and cleaned data
src/heart_ml/       Reusable preparation, training, and API code
tests/              Unit tests
models/             Serialized selected pipeline and metadata after training
reports/            EDA/model figures and metrics after training
.github/workflows/  CI pipeline
k8s/                Kubernetes deployment manifests
monitoring/         Prometheus scrape configuration
```

## Important note

This classifier is an educational project, not a medical device. It must not be used to diagnose, treat, or make clinical decisions for any individual.
