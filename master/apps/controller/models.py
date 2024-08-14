class Task:
    def __init__(self, id):
        self.id = id
        self.state = "NEW"
        self.__input_exec_time_map = {}

    def is_ready(self):
        if len(self.__input_exec_time_map.keys()) != 0:
            self.state = "READY"

        return (self.state == "READY")

    def input_exists(self, input_size):
        return (input_size in self.__input_exec_time_map.keys())

    def set_exec_time_for_input(self, input_size, exec_time_map):
        self.__input_exec_time_map[input_size] = exec_time_map

    def get_exec_time_for_input(self, input_size):
        return self.__input_exec_time_map[input_size]
