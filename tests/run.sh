#! /bin/bash

cd ../master/
source .venv/bin/activate
make gunicorn-cluster-manager& gunicorn-controller& gunicorn-scheduler& gunicorn-predictor&
deactivate

cd ../worker/
make start-worker

cd ../tests/
source .venv/bin/activate
python main.py
deactivate
