.PHONY: prepare train test lint serve docker-build

prepare:
	python scripts/prepare_data.py

train:
	python -m heart_ml.train --data data/cleaned/heart_disease_cleaned.csv

test:
	pytest -q

lint:
	ruff check src tests scripts

serve:
	uvicorn heart_ml.api:app --host 0.0.0.0 --port 8000

docker-build:
	docker build -t heart-disease-api:local .
