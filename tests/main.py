import csv
import time

from client.http import HTTPClient


TEST_ITER = 10
FUNCTION_DIR = "./functions"

MANAGER_URL = "http://localhost:8100"
SCHEDULER_URL = "http://localhost:8000"
CONTROLLER_URL = "http://localhost:8200"
CLIENT_DELAY_SECONDS = 0.1

WORKER_SLEEP_DURATION = 10
WORKER_HOSTS = ["http://localhost:3000"]

FUNCTIONS = [
    {
        "command": "python3.10",
        "filepath": "batch-normalization/batch_normalization-2000000.py",
    },
]

client = HTTPClient(CLIENT_DELAY_SECONDS, MANAGER_URL, SCHEDULER_URL, CONTROLLER_URL)

def write_to_file(values, filepath):
    with open(filepath, "a") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(values)

def test_scenario():
    for host in WORKER_HOSTS:
        assert client.register_worker(host)

    time.sleep(WORKER_SLEEP_DURATION)

    for function in FUNCTIONS:
        command = function["command"]
        filepath = f"{FUNCTION_DIR}/{function['filepath']}"

        filename = filepath.rsplit("/", 1)[1][:-3]
        function_name, input_size = filename.split("-")

        generosity = client.get_generosity()

        task_id = client.new_task(filepath)

        resp = client.benchmark_task(command, task_id)
        assert resp["message"] == "Benchmarking was successful and function is ready for execution"

        cos_exec_time_map = resp["exec_time"]

        for cos, exec_time in cos_exec_time_map.items():
            write_to_file([function_name, input_size, cos, exec_time], "./results/bench_output.csv")

        for _ in range(TEST_ITER):
            cos, exec_time = client.run_task(command, task_id)
            write_to_file([function_name, input_size, cos, exec_time, generosity], "./results/run_output.csv")


if __name__ == "__main__":
    # this is the best stupid idea i've ever had
    _ = input()

    try:
        test_scenario()
        print(f"Testing Successful")

    except Exception as err:
        print(f"testing Failed With The Following Error: {err}")
