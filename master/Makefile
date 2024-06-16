install-deps:
	pip install -r requirements.txt

gunicorn-api-server:
	gunicorn --bind=0.0.0.0:$(GUNICORN_API_PORT) --timeout=$(GUNICORN_API_TIMEOUT) --workers=$(GUNICORN_API_WORKERS) --reload apps.api.app:app

gunicorn-cluster-manager:
	gunicorn --bind=0.0.0.0:$(GUNICORN_CLUSTER_PORT) --timeout=$(GUNICORN_CLUSTER_TIMEOUT) --workers=$(GUNICORN_CLUSTER_WORKERS) --reload apps.cluster.app:app


GUNICORN_API_WORKERS ?= 1
GUNICORN_API_TIMEOUT ?= 5000
GUNICORN_API_PORT ?= 8000

GUNICORN_CLUSTER_WORKERS ?= 1
GUNICORN_CLUSTER_TIMEOUT ?= 5000
GUNICORN_CLUSTER_PORT ?= 8100
