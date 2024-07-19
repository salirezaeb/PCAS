import time
import threading

import requests
from sortedcontainers import SortedSet

from config import Config


class Scheduler:
    # FIXME: pass config as argument to constructor instead of reading directly from Config
    def __init__(self):
        self.manager_host = Config.MANAGER_HOST
        self.update_interval = Config.UPDATE_INTERVAL_SECONDS
        self.__worker_pool = SortedSet(key=lambda x: x[0])
        self.__total_available_cache = 0
        self.__worker_pool_lock = threading.Lock()
        self.__generosity_variable = 0
        self.__generosity_lock = threading.Lock()
        self.__session = requests.Session()

    def __calculate_generosity(self):
        # TODO: this is some simple test formula but it works alright for now
        with self.__worker_pool_lock:
            generosity_variable = -1 / (max(self.__total_available_cache, 20) / 2)

        with self.__generosity_lock:
            self.__generosity_variable = generosity_variable

    def get_generosity_variable(self):
        with self.__generosity_lock:
            return self.__generosity_variable

    def __update_worker_info(self):
        url = f"{self.manager_host}/cluster/worker/list"

        resp = self.__session.get(url)
        resp.raise_for_status()

        json_data = resp.json()

        # FIXME: handle edge cases
        with self.__worker_pool_lock:
            self.__worker_pool.clear()
            self.__total_available_cache = 0

            for (id, resource) in json_data.items():
                if resource is not None:
                    available_cache = resource["free_cache"]

                    self.__worker_pool.add((available_cache, id))
                    self.__total_available_cache += available_cache

    def daemon(self):
        while True:
            self.__update_worker_info()
            self.__calculate_generosity()

            time.sleep(self.update_interval)

    # TODO: this is a dummy method for testing purposes
    def dummy_choose_suitable_worker(self, task_id):
        with self.__worker_pool_lock:
            return (self.__worker_pool[0] if len(self.__worker_pool) != 0 else None)

    def choose_suitable_worker(self, task_id, cos):
        with self.__worker_pool_lock:
            # TODO: remove print lines below
            print(f"total_cache: {self.__total_available_cache}")
            print(f"worker_pool: {self.__worker_pool}")

            index = self.__worker_pool.bisect_left((cos, ""))
            if index >= len(self.__worker_pool):
                return None

            _, worker_id = self.__worker_pool.pop(index)

            return worker_id
