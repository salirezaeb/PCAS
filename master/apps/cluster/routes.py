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

@routes_bp.route("/cluster/generosity", methods=["GET"])
def get_generosity():
    generosity_variable = cluster_manager.get_generosity_variable()

    return jsonify({"generosity": generosity_variable}), 200
