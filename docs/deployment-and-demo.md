# Deployment and Demo Evidence

## Local container proof

1. Run `docker compose up --build`.
2. Capture a terminal screenshot showing both `api` and `prometheus` running.
3. Open `http://localhost:8000/docs`, use `POST /predict`, and capture the response.
4. Open `http://localhost:9090`, query `heart_predictions_total`, and capture the result.

## Kubernetes proof

1. Build and push the image, then replace the placeholder registry name in `k8s/deployment.yaml`.
2. Apply the four manifests in the README.
3. Capture `kubectl -n heart-ml get pods,svc,hpa`.
4. Capture the exposed endpoint response from `/health` and `/predict`.

## Short video structure

Keep the recording to 3-5 minutes: show the repository structure, run tests, show MLflow runs, demonstrate the Docker API request, show Prometheus metrics, then show Kubernetes resources. Narrate the role of the fitted preprocessing pipeline and why it prevents training-serving skew.
