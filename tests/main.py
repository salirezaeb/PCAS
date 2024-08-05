import csv

from client.http import HTTPClient


TEST_ITER = 5
FUNCTION_DIR = "./tests/functions"
OUTPUT_FILE = "./results/output.csv"

MANAGER_URL = "TODO"
SCHEDULER_URL = "TODO"
CONTROLLER_URL = "TODO"

WORKER_HOSTS = ["TODO"]
FUNCTIONS = [
    {
        command: "TODO",
        filepath: "TODO",
    },
]

client = HTTPClient(BASE_URL)

def write_to_file(function_name, input_size, cos, exec_time, generosity):
    with open(OUTPUT_FILE, "a") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow([function_name, input_size, cos, exec_time, generosity])

def test_scenario():
    for host in WORKER_HOSTS:
        assert client.register_worker(host)

    for function in FUNCTIONS:
        command = function["command"]
        filepath = f"{FUNCTION_DIR}/{function['filepath']}"

        filename = filepath.rsplit("/", 1)[1][:-3]
        function_name, input_size = filename.split("-")

        generosity = client.get_generosity()

        task_id = client.new_task(filepath)
        assert client.benchmark_task(command, task_id)

        for _ in range(TEST_ITER):
            cos, exec_time = client.run_task(command, task_id)
            write_to_file(function_name, input_size, cos, exec_time, generosity)


if __name__ == "__main__":
    try:
        test_scenario()
        print(f"Testing Successful")

    except Exception as err:
        print(f"testing Failed With The Following Error: {err}")
