from apps.predictor import cache_predictor

from flask import Blueprint, request, jsonify


routes_bp = Blueprint("routes", __name__)

# FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
@routes_bp.route("/predictor/task", methods=["POST"])
def predict_task_cache_requirements():
    json_data = request.get_json()

    required_keys = ["task_id", "generosity", "result"]

    for key in required_keys:
        if key not in json_data.keys():
            return jsonify({"message": "Required keys not specified"}), 400

    task_id = json_data["task_id"]
    generosity = json_data["generosity"]
    cos_exec_map = json_data["result"]

    suitable_cos, pred_exec_time = cache_predictor.predict_for_function(task_id, generosity, cos_exec_map)

    return jsonify({"suitable_cos": suitable_cos}), 200
