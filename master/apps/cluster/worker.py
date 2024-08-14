import requests

from dataclasses import dataclass

from fs import filesystem


@dataclass
class SystemInfo:
    cpu_cores: int
    free_ram: int
    total_ram: int
    used_ram: int
    free_swap: int
    total_swap: int
    used_swap: int
    free_cache: int
    total_cache: int
    used_cache: int


class WorkerNode:
    def __init__(self, host):
        self.host = host
        self.system_info = None
        self.__fs = filesystem.Handler()
        self.__session = requests.Session()

    def raise_if_unresponsive(self):
        url = f"{self.host}/task/count"

        resp = self.__session.get(url)
        resp.raise_for_status()

    def retrieve_system_info(self):
        url = f"{self.host}/system/info"

        resp = self.__session.get(url)
        resp.raise_for_status()

        json_data = resp.json()
        self.system_info = SystemInfo(**json_data)

    def load_task(self, task_id):
        url = f"{self.host}/task/file/new"

        files = { "file": self.__fs.get_handle(task_id) }

        resp = self.__session.post(url, files=files)
        resp.raise_for_status()

        json_data = resp.json()

        return json_data["id"]

    def run_task(self, command, id, input_size, cos):
        url = f"{self.host}/task/file/run"

        headers = {"Content-Type": "application/json"}

        payload = {
            "command": command,
            "filename": id,
            "input_size": input_size,
            # "cos": cos,
            "cos": 0,
        }

        resp = self.__session.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        return resp.json()
