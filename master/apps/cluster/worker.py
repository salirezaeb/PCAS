import requests

from dataclasses import dataclass


@dataclass
class SystemInfo:
    cpu_cores: int
    free_ram: int
    total_ram: int
    used_ram: int
    free_swap: int
    total_swap: int
    used_swap: int


class WorkerNode:
    def __init__(self, host):
        self.host = host
        self.__session = requests.Session()
        self.system_info = None

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
