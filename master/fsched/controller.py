import requests

from config import Config

from fsched.fs import FileSystem


class Controller:
    # FIXME: pass config as argument to constructor instead of reading directly from Config
    def __init__(self):
        self.task_state = {}
        self.task_exec_time = {}
        self.cos_count = Config.COS_COUNT
        self.manager_host = Config.MANAGER_HOST
        self.scheduler_host = Config.SCHEDULER_HOST
        self.predictor_host = Config.PREDICTOR_HOST
        self.__fs = FileSystem()
        self.__session = requests.Session()

    def create_task(self, file):
        task_id = self.__fs.create_file(file)
        self.task_state[task_id] = "NEW"

        return task_id

    def task_is_ready(self, task_id):
        return (self.task_state[task_id] == "READY")

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

        return json_data["worker_id"]

    # FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
    def __execution_helper(self, command, task_id, cos):
        url = f"{self.manager_host}/cluster/task/assign"

        headers = {"Content-Type": "application/json"}

        payload = {
            "command": command,
            "task_id": task_id,
            "worker_id": self.__find_suitable_worker(task_id, cos),
            "cos": cos,
        }

        resp = self.__session.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        return resp

    # FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
    def assign_benchmark(self, command, task_id):
        cos_exec_time_map = {}

        for cos in range(1, self.cos_count):
            resp = self.__execution_helper(command, task_id, cos)
            json_data = resp.json()["result"]

            # FIXME: use exceptions here
            if json_data["exit_status"] != 0:
                return

            json_exec = json_data["execution_time"]

            cos_exec_time_map[cos] = json_exec["secs"] + json_exec["nanos"] / 1e9

        self.task_state[task_id] = "READY"
        self.task_exec_time[task_id] = cos_exec_time_map

    def __get_generosity_variable(self):
        url = f"{self.scheduler_host}/scheduler/generosity"

        resp = self.__session.get(url)
        resp.raise_for_status()

        json_data = resp.json()
        generosity = float(json_data["generosity"])

        return generosity

    # FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
    def __llc_prediction(self, task_id, generosity, cos_exec_time_map):
        url = f"{self.predictor_host}/predictor/task"

        headers = {"Content-Type": "application/json"}

        payload = {
            "task_id": task_id,
            "generosity": generosity,
            "execution_time_list": [exec_time for exec_time in cos_exec_time_map.values()],
        }

        resp = self.__session.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        json_data = resp.json()

        return json_data["suitable_cos"]

    # FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
    def assign_execution(self, command, task_id):
        generosity = self.__get_generosity_variable()
        suitable_cos = self.__llc_prediction(task_id, generosity, self.task_exec_time[task_id])
        resp = self.__execution_helper(command, task_id, suitable_cos)

        return resp
