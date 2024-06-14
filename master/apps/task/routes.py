from flask import Blueprint, request, jsonify


routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/api/task/new", methods=["POST"])
def request_new():
    req = request.json

    return (jsonify({"message": req}), 200)
