from apps.api_server import cluster_manager

from flask import Blueprint, request, jsonify


routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/api/worker/add", methods=["POST"])
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

@routes_bp.route("/api/task/new", methods=["POST"])
def new_task():
    if "command" not in request.form:
        return jsonify({"error": "File and command are required"}), 400

    if "file" not in request.files:
        pass
        # TODO

    file = request.files['file']
    command = request.form['command']
    # TODO
