from flask import Blueprint, request, jsonify


routes_bp = Blueprint("routes", __name__)

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
