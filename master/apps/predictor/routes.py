from apps.predictor import cache_predictor

from flask import Blueprint, request, jsonify


routes_bp = Blueprint("routes", __name__)

# FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
@routes_bp.route("/predictor/task/benchmarked", methods=["POST"])
def predict_benchmarked_task_cache_requirements():
    json_data = request.get_json()

    required_keys = ["task_id", "input_size", "generosity", "execution_time_list"]

    for key in required_keys:
        if key not in json_data.keys():
            return jsonify({"message": "Required keys not specified"}), 400

    task_id = json_data["task_id"]
    input_size = json_data["input_size"]
    generosity = json_data["generosity"]
    function_exec_times = json_data["execution_time_list"]

    suitable_cos = cache_predictor.predict_for_benchmarked_task(task_id, input_size, generosity, function_exec_times)

    return jsonify({"suitable_cos": suitable_cos}), 200

# FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
@routes_bp.route("/predictor/task/assisted", methods=["POST"])
def predict_assisted_task_cache_requirements():
    json_data = request.get_json()

    required_keys = ["task_id", "input_size", "generosity"]

    for key in required_keys:
        if key not in json_data.keys():
            return jsonify({"message": "Required keys not specified"}), 400

    task_id = json_data["task_id"]
    input_size = json_data["input_size"]
    generosity = json_data["generosity"]

    suitable_cos = cache_predictor.predict_for_assisted_task(task_id, input_size, generosity)

    return jsonify({"suitable_cos": suitable_cos}), 200
