from apps.cluster import cluster_manager

from flask import Blueprint, request, jsonify


routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/cluster/worker/add", methods=["POST"])
def add_worker():
    json_data = request.get_json()

    if "host" not in json_data:
        return jsonify({"message": "no worker host specified"}), 400

    host = json_data.get("host")

    try:
        cluster_manager.add_worker(host)

    except Exception:
        return jsonify({"message": "worker node is unresponsive"}), 500

    return jsonify({"message": "worker node successfully added"}), 200

@routes_bp.route("/cluster/worker/list", methods=["GET"])
def list_workers():
    worker_id_map = cluster_manager.list_workers()

    return jsonify(worker_id_map), 200

# FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
@routes_bp.route("/cluster/task/assign", methods=["POST"])
def assign_task_to_worker():
    json_data = request.get_json()

    required_keys = ["cos", "command", "task_id", "worker_id"]

    for key in required_keys:
        if key not in json_data.keys():
            return jsonify({"message": "Required keys not specified"}), 400

    cos = json_data["cos"]
    command = json_data["command"]
    task_id = json_data["task_id"]
    worker_id = json_data["worker_id"]

    res = cluster_manager.assign_task_execution(worker_id, command, task_id, cos)

    return jsonify({"result": res}), 200
