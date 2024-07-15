from apps.scheduler import fs

from flask import Blueprint, request, jsonify


routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/scheduler/task/new", methods=["POST"])
def new_task():
    if "file" not in request.files:
        return jsonify({"message": "No file specified"}), 400

    file = request.files['file']

    filename = fs.create_file(file)

    return jsonify({"message": f"{filename}"}), 200

@routes_bp.route("/scheduler/task/run", methods=["POST"])
def run_task():
    json_data = request.get_json()

    if "command" or "filename" not in json_data:
        return jsonify({"message": "No command or filename specified"}), 400

    # TODO: post to worker

    return jsonify({"message": "Ok!"}), 200
