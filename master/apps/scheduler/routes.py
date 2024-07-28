from apps.scheduler import fs, scheduler

from flask import Blueprint, request, jsonify


routes_bp = Blueprint("routes", __name__)


@routes_bp.route("/scheduler/generosity", methods=["GET"])
def get_generosity():
    generosity_variable = scheduler.get_generosity_variable()

    return jsonify({"generosity": generosity_variable}), 200

# FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
@routes_bp.route("/scheduler/task/worker", methods=["POST"])
def get_suitable_worker():
    json_data = request.get_json()

    required_keys = ["task_id", "cos"]

    for key in required_keys:
        if key not in json_data.keys():
            return jsonify({"message": "Required keys not specified"}), 400

    cos = json_data["cos"]
    task_id = json_data["task_id"]

    worker_id, cos = scheduler.choose_suitable_worker(task_id, cos)

    return jsonify({"worker_id": worker_id, "cos": cos}), 200
