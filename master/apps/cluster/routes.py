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

    print(json_data)

    if "filename" not in json_data.keys() or "worker_id" not in json_data.keys():
        return jsonify({"message": "No filename or worker_id specified"}), 400

    # TODO

    return jsonify({"message": "Ok!"}), 200
