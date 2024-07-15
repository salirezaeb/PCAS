import time
import threading

import requests

from config import Config


class Scheduler:
    def __init__(self):
        self.worker_resource_map = {}
        self.manager_host = Config.MANAGER_HOST
        self.update_interval = Config.UPDATE_INTERVAL_SECONDS
        self.__generosity_variable = 0
        self.__generosity_lock = threading.Lock()
        self.__session = requests.Session()

    def __calculate_generosity(self):
        cluster_free_cache = sum([worker["free_cache"] for worker in self.worker_resource_map.values()])
        generosity_variable = -1 / (max(cluster_free_cache, 20) / 2)

        with self.__generosity_lock:
            self.__generosity_variable = generosity_variable

    def get_generosity_variable(self):
        with self.__generosity_lock:
            return self.__generosity_variable

    def update_worker_info(self):
        url = f"{self.manager_host}/cluster/worker/list"

        resp = self.__session.get(url)
        resp.raise_for_status()

        self.worker_resource_map = { id: resource for (id, resource) in resp.json().items() if resource is not None }

    def daemon(self):
        while True:
            self.update_worker_info()
            self.__calculate_generosity()

            time.sleep(self.update_interval)

    def __choose_suitable_worker(self, filepath):
        # TODO: this is for testing purposes
        keys = list(self.worker_resource_map.keys())
        return (keys[0] if len(keys) != 0 else None)

    # FIXME: this uses REST for now, in the future it should be implemented using smth event-based (eg: rabbitmq)
    def schedule(self, command, filepath):
        url = f"{self.manager_host}/cluster/task/assign"

        headers = {"Content-Type": "application/json"}

        payload = {
            "command": command,
            "filepath": filepath,
            "worker_id": self.__choose_suitable_worker(filepath),
        }

        resp = self.__session.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        return resp
