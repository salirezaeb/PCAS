import time
import threading
import uuid

from fsched.worker import WorkerNode
from config import Config


class ClusterManager:
    def __init__(self):
        self.worker_id_map = {}
        self.SCRAPE_INTERVAL = Config.SCRAPE_INTERVAL_SECONDS
        self.__generosity_variable = 0
        self.__generosity_lock = threading.Lock()

    def __calculate_generosity(self):
        cluster_free_cache = sum([worker.system_info.free_cache for worker in self.worker_id_map.values()])
        generosity_variable = -1 / (max(cluster_free_cache, 20) / 2)

        with self.__generosity_lock:
            self.__generosity_variable = generosity_variable

    def get_generosity_variable(self):
        with self.__generosity_lock:
            return self.__generosity_variable

    def add_worker(self, worker_host):
        id = uuid.uuid4()
        worker_node = WorkerNode(worker_host)

        worker_node.raise_if_unresponsive()

        self.worker_id_map[id] = worker_node

    def scrape_workers(self):
        while True:
            threads = []
            workers = self.worker_id_map.values()
            for worker in workers:
                thread = threading.Thread(target=worker.retrieve_system_info)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            self.__calculate_generosity()
            time.sleep(self.SCRAPE_INTERVAL)

    def assign_task_to_worker(self, worker_id):
        worker = self.worker_id_map[worker_id]
        pass # TODO
