import requests

from config import Config

from fsched.fs import FileSystem


class Controller:
    # FIXME: pass config as argument to constructor instead of reading directly from Config
    def __init__(self):
        self.task_state = {}
        self.cos_count = Config.COS_COUNT
        self.manager_host = Config.MANAGER_HOST
        self.scheduler_host = Config.SCHEDULER_HOST
        self.__fs = FileSystem()
        self.__session = requests.Session()

    def create_task(self, file):
        task_id = self.__fs.create_file(file)
        self.task_state[task_id] = "NEW"

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
    def assign_execution(self, command, task_id):
        url = f"{self.manager_host}/cluster/task/assign"

        headers = {"Content-Type": "application/json"}

        payload = {
            "command": command,
            "task_id": task_id,
            "worker_id": self.__find_suitable_worker(task_id),
            # TODO: "cos": cos,
        }

        resp = self.__session.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        return resp

    # FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
    def assign_benchmark(self, command, task_id):
        exec_time = {}

        for cos in range(1, self.cos_count + 1):
            resp = self.assign_execution(command, task_id)
            json_data = resp.json()["result"]

            if json_data["exit_status"] != 0:
                raise Exception("failed to benchmark the task with specified command")

            json_exec = json_data["execution_time"]

            exec_time[cos] = json_exec["secs"] + json_exec["nanos"] / 1e9

        self.task_state[task_id] = "READY"

        return exec_time
