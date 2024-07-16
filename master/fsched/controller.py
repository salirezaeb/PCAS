import requests

from config import Config

from fsched.fs import FileSystem


class Controller:
    # FIXME: pass config as argument to constructor instead of reading directly from Config
    def __init__(self):
        self.task_state = {}
        self.manager_host = Config.MANAGER_HOST
        self.scheduler_host = Config.SCHEDULER_HOST
        self.__fs = FileSystem()
        self.__session = requests.Session()

    def create_task(self, file):
        task_id = self.__fs.create_file(file)
        self.task_state[task_id] = "READY"

        return task_id

    def task_is_ready(self, task_id):
        return (self.task_state[task_id] == "READY")

    def __find_suitable_worker(self, task_id):
        url = f"{self.scheduler_host}/scheduler/task/worker"

        headers = {"Content-Type": "application/json"}

        payload = {"task_id": task_id}

        resp = self.__session.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        json_data = resp.json()

        return json_data["worker_id"]

    # FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
    def assign_benchmark(self, task_id):
        pass

    # FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
    def assign_execution(self, command, task_id):
        url = f"{self.manager_host}/cluster/task/assign"

        headers = {"Content-Type": "application/json"}


        payload = {
            "command": command,
            "task_id": task_id,
            "worker_id": self.__find_suitable_worker(task_id),
        }

        resp = self.__session.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        return resp
