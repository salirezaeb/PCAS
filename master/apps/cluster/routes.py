from apps.cluster import cluster_manager

from flask import Blueprint, request, jsonify


routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/worker/add", methods=["POST"])
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
