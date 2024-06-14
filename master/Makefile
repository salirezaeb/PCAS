install-deps:
	pip install -r requirements.txt

gunicorn-task-app:
	gunicorn --bind=0.0.0.0:$(GUNICORN_TASK_PORT) --timeout=$(GUNICORN_TASK_TIMEOUT) --workers=$(GUNICORN_TASK_WORKERS) --reload apps.task.app:app


GUNICORN_TASK_WORKERS ?= 1
GUNICORN_TASK_TIMEOUT ?= 5000
GUNICORN_TASK_PORT ?= 8000
