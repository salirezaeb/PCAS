class Task:
    def __init__(self, id):
        self.id = id
        self.__input_exec_time_map = {}

    def state_for_input(self, input_size):
        if len(self.__input_exec_time_map.keys()) == 0:
            return "INOP"

        if input_size not in self.__input_exec_time_map.keys():
            return "ASSISTED"

        return "BENCHMARKED"

    def set_exec_time_for_input(self, input_size, exec_time_map):
        self.__input_exec_time_map[input_size] = exec_time_map

    def get_exec_time_for_input(self, input_size):
        return self.__input_exec_time_map[input_size]
