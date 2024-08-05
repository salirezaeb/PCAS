import requests


class HTTPClient:
    def __init__(self, manager_url, scheduler_url, controller_url):
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

    def get_generosity(self):
        url = f"{self.scheduler_url}/scheduler/generosity"

        response = requests.get(url)
        response.raise_for_status()

        json_data = response.json()
        return json_data["generosity"]

    def new_task(self, filename):
        url = f"{self.controller_url}/task/new"

        filepath = f"{result_dir}/{filename}"

        with open(filepath, "rb") as file:
            files = {"file": file}

            response = requests.post(url, files=files)
            response.raise_for_status()

            json_data = response.json()
            return json_data["task_id"]

    def benchmark_task(self, command, task_id):
        url = f"{self.controller_url}/task/benchmark"

        headers = {"Content-Type": "application/json"}

        payload = {
            "task_id": task_id,
            "command": command,
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        json_data = response.json()
        return (json_data["message"] == "Benchmarking was successful and function is ready for execution")

    def run_task(self, command, task_id):
        url = f"{self.controller_url}/task/run"

        headers = {"Content-Type": "application/json"}

        payload = {
            "task_id": task_id,
            "command": command,
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        json_data = response.json()
        result = json_data["result"]

        cos = result["cos"]
        exec_time = result["execution_time"]["secs"] + (1000000000 * result["execution_time"]["nanos"])

        return cos, exec_time
