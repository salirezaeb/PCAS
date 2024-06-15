import time
import threading
import uuid

from apps.cluster.worker import WorkerNode


class ClusterManager:
    def __init__(self, scrape_interval):
        self.worker_id_map = {}
        self.SCRAPE_INTERVAL = scrape_interval

    def add_worker(self, worker_host):
        id = uuid.uuid4()
        worker_node = WorkerNode(worker_host)

        worker_node.raise_if_unresponsive()

        self.worker_id_map[id] = worker_node

    def scrape_workers(self):
        while True:
            workers = self.worker_id_map.values()
            for worker in workers:
                threading.Thread(target=worker.retrieve_system_info).start()

            time.sleep(self.SCRAPE_INTERVAL)
