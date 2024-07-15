import time
import uuid
import threading

from config import Config

from fsched.worker import WorkerNode


class ClusterManager:
    def __init__(self):
        self.worker_id_map = {}
        self.scrape_interval = Config.SCRAPE_INTERVAL_SECONDS

    def add_worker(self, worker_host):
        id = str(uuid.uuid4())
        worker_node = WorkerNode(worker_host)

        worker_node.raise_if_unresponsive()

        self.worker_id_map[id] = worker_node

    def list_workers(self):
        return {id: worker.system_info for (id, worker) in self.worker_id_map.items()}

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

            time.sleep(self.scrape_interval)

    def assign_task_to_worker(self, worker_id, command, filepath):
        worker = self.worker_id_map[worker_id]

        id = worker.upload_file(filepath)
        res = worker.run_task(command, id)

        return res
