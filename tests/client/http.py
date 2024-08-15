import time
import requests


class HTTPClient:
    def __init__(self, delay_seconds, manager_url, scheduler_url, controller_url):
        self.delay_seconds = delay_seconds
        self.manager_url = manager_url
        self.scheduler_url = scheduler_url
        self.controller_url = controller_url

    def register_worker(self, host):
        url = f"{self.manager_url}/cluster/worker/add"

        headers = {"Content-Type": "application/json"}

        payload = {
            "host": host,
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        json_data = response.json()
        return (json_data["message"] == "worker node successfully added")

    def list_workers(self):
        url = f"{self.manager_url}/cluster/worker/list"

        response = requests.get(url)
        response.raise_for_status()

        return response.json()

    def get_generosity(self):
        url = f"{self.scheduler_url}/scheduler/generosity"

        response = requests.get(url)
        response.raise_for_status()

        json_data = response.json()
        return json_data["generosity"]

    def new_task(self, filepath):
        url = f"{self.controller_url}/controller/task/new"

        with open(filepath, "rb") as file:
            files = {"file": file}

            response = requests.post(url, files=files)
            response.raise_for_status()

            json_data = response.json()
            return json_data["task_id"]

    def benchmark_task(self, command, task_id, input_size):
        url = f"{self.controller_url}/controller/task/benchmark"

        headers = {"Content-Type": "application/json"}

        payload = {
            "task_id": task_id,
            "command": command,
            "input_size": input_size,
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        time.sleep(self.delay_seconds)

        return response.json()

    def run_task(self, command, task_id, input_size):
        url = f"{self.controller_url}/controller/task/run"

        headers = {"Content-Type": "application/json"}

        payload = {
            "task_id": task_id,
            "command": command,
            "input_size": input_size,
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        time.sleep(self.delay_seconds)

        json_data = response.json()

        mode = json_data["mode"]
        result = json_data["result"]

        cos = result["cos"]
        exec_time = result["execution_time"]["secs"] + (1e-9 * result["execution_time"]["nanos"])

        return mode, cos, exec_time
