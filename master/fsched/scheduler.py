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
