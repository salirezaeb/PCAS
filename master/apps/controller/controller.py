import requests

from config import Config

from fs import filesystem
from apps.controller import models


class Controller:
    # FIXME: pass config as argument to constructor instead of reading directly from Config
    def __init__(self):
        self.cos_count = Config.COS_COUNT
        self.manager_host = Config.MANAGER_HOST
        self.scheduler_host = Config.SCHEDULER_HOST
        self.predictor_host = Config.PREDICTOR_HOST
        self.__fs = filesystem.Handler()
        self.__session = requests.Session()
        self.__task_map = {}

    def create_task(self, file):
        id = self.__fs.create_file(file)
        self.__task_map[id] = models.Task(id)

        return id

    def task_state_for_input(self, task_id, input_size):
        return self.__task_map[task_id].state_for_input(input_size)

    def __find_suitable_worker(self, task_id, cos):
        url = f"{self.scheduler_host}/scheduler/task/worker"

        headers = {"Content-Type": "application/json"}

        payload = {
            "task_id": task_id,
            "cos": cos,
        }

        resp = self.__session.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        json_data = resp.json()

        return json_data["worker_id"], json_data["cos"]

    # FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
    def __execution_helper(self, command, task_id, input_size, cos):
        url = f"{self.manager_host}/cluster/task/assign"

        headers = {"Content-Type": "application/json"}

        worker_id, worker_cos = self.__find_suitable_worker(task_id, cos)

        payload = {
            "command": command,
            "task_id": task_id,
            "worker_id": worker_id,
            "input_size": input_size,
            "cos": min(cos, worker_cos),
        }

        resp = self.__session.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        return resp

    # FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
    def assign_benchmark(self, command, task_id, input_size):
        exec_time_map = {}

        for cos in range(1, self.cos_count + 1):
            resp = self.__execution_helper(command, task_id, input_size, cos)
            json_data = resp.json()["result"]

            # FIXME: use exceptions here
            if json_data["exit_status"] != 0:
                return

            json_exec = json_data["execution_time"]

            exec_time_map[cos] = json_exec["secs"] + json_exec["nanos"] / 1e9

        task = self.__task_map[task_id]
        task.set_exec_time_for_input(input_size, exec_time_map)

        return exec_time_map

    def __get_generosity_variable(self):
        url = f"{self.scheduler_host}/scheduler/generosity"

        resp = self.__session.get(url)
        resp.raise_for_status()

        json_data = resp.json()
        generosity = float(json_data["generosity"])

        return generosity

    # FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
    def __llc_prediction(self, task_id, input_size, generosity):
        url = f"{self.predictor_host}/predictor/task"

        headers = {"Content-Type": "application/json"}

        task = self.__task_map[task_id]

        if task.state_for_input(input_size) == "ASSISTED":
            url = f"{url}/assisted"

            payload = {
                "task_id": task_id,
                "generosity": generosity,
                "input_size": input_size,
            }

        if task.state_for_input(input_size) == "BENCHMARKED":
            url = f"{url}/benchmarked"

            exec_time_map = task.get_exec_time_for_input(input_size)

            payload = {
                "task_id": task_id,
                "generosity": generosity,
                "input_size": input_size,
                "execution_time_list": [exec_time for exec_time in exec_time_map.values()],
            }

        resp = self.__session.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        json_data = resp.json()

        return json_data["suitable_cos"]

    # FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
    def assign_execution(self, command, task_id, input_size):
        generosity = self.__get_generosity_variable()
        suitable_cos = self.__llc_prediction(task_id, input_size, generosity)
        resp = self.__execution_helper(command, task_id, input_size, suitable_cos)

        return resp
