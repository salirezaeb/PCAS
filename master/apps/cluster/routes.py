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

    required_keys = ["command", "filepath", "worker_id"]

    for key in required_keys:
        if key not in json_data.keys():
            return jsonify({"message": "Required keys not specified"}), 400

    command = json_data["command"]
    filepath = json_data["filepath"]
    worker_id = json_data["worker_id"]

    res = cluster_manager.assign_task_to_worker(worker_id, command, filepath)

    return jsonify({"result": res}), 200
