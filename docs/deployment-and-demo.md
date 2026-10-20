# Deployment and Demo Evidence

## Current submission status

- A public API URL has not been deployed. The API is ready for local testing at
  `http://localhost:8000` using the README quick-start instructions.
- The repository contains the report and automated EDA/model figures. Capture
  the live-run screenshots below; do not present placeholder images as run
  evidence.
- Record the 3-5 minute video below after running the pipeline. Save the final
  recording as `video/pipeline-demo.mp4` (or include an accessible video link
  with the submission).

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

Keep the recording to 3-5 minutes:

1. Introduce the repository and dataset preparation.
2. Run the unit tests and show the EDA/training output and MLflow runs.
3. Demonstrate a sample request to the Dockerized API.
4. Show Prometheus metrics and, if Kubernetes is available, the deployed
   resources.
5. Explain that the fitted preprocessing pipeline is shared between training
   and serving to reduce training-serving skew.

If a cloud endpoint is unavailable, explicitly demonstrate the local endpoint
and mention that no public service is deployed. Do not claim cloud deployment
without a reachable endpoint and corresponding evidence.
