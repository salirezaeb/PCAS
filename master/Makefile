install-deps:
	pip install -r requirements.txt

gunicorn-scheduler:
	gunicorn --bind=0.0.0.0:$(GUNICORN_SCHEDULER_PORT) --timeout=$(GUNICORN_SCHEDULER_TIMEOUT) --workers=$(GUNICORN_SCHEDULER_WORKERS) --reload apps.scheduler.app:app

gunicorn-cluster-manager:
	gunicorn --bind=0.0.0.0:$(GUNICORN_CLUSTER_PORT) --timeout=$(GUNICORN_CLUSTER_TIMEOUT) --workers=$(GUNICORN_CLUSTER_WORKERS) --reload apps.cluster.app:app


GUNICORN_SCHEDULER_WORKERS ?= 1
GUNICORN_SCHEDULER_TIMEOUT ?= 5000
GUNICORN_SCHEDULER_PORT ?= 8000

GUNICORN_CLUSTER_WORKERS ?= 1
GUNICORN_CLUSTER_TIMEOUT ?= 5000
GUNICORN_CLUSTER_PORT ?= 8100
