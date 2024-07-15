from apps.scheduler import fs, scheduler

from flask import Blueprint, request, jsonify


routes_bp = Blueprint("routes", __name__)


@routes_bp.route("/scheduler/generosity", methods=["GET"])
def get_generosity():
    generosity_variable = scheduler.get_generosity_variable()

    return jsonify({"generosity": generosity_variable}), 200

@routes_bp.route("/scheduler/task/new", methods=["POST"])
def new_task():
    if "file" not in request.files:
        return jsonify({"message": "No file specified"}), 400

    file = request.files['file']

    filename = fs.create_file(file)

    return jsonify({"message": f"{filename}"}), 200

# FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
@routes_bp.route("/scheduler/task/run", methods=["POST"])
def run_task():
    json_data = request.get_json()

    if "command" not in json_data.keys() or "filename" not in json_data.keys():
        return jsonify({"message": "No command or filename specified"}), 400

    filename = json_data["filename"]
    scheduler.schedule(filename)

    return jsonify({"message": "Ok!"}), 200
