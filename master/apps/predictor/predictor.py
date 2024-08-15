from config import Config

from db.csv import CSVAdapter


class CachePredictor:
    # FIXME: pass config as argument to constructor instead of reading directly from Config
    def __init__(self):
        # FIXME: reading csv file for now will switch to db later
        self.__db = CSVAdapter()
        self.__task_input_map = {}
        self.__model = None

    @staticmethod
    def __run_mse(model_exec_times, function_exec_times):
        return sum((yt - yp) ** 2 for yt, yp in zip(model_exec_times, function_exec_times))

    def __find_corresponding_model_with_exec_times(self, function_exec_times):
        target = (None, None, None, None)
        for (key, val) in self.__model.items():
            model_exec_times, x_model, y_model = val

            reg_exec_times = self.__db.fit_regression(function_exec_times)

            _, min_mse, _, _ = target
            mse = self.__run_mse(model_exec_times, reg_exec_times)

            if min_mse is None or mse < min_mse:
                target = (key, mse, x_model, y_model)

        rep_func, _, suitable_cos, _ = target

        return (rep_func, suitable_cos)

    def __find_corresponding_model_with_input_size(self, task_id, input_size):
        task_map = self.__task_input_map[task_id]

        nearest_input_size = min(task_map.keys(), key=lambda x:abs(int(x[1]) - int(input_size)))

        target_name, rep_size = task_map[nearest_input_size]
        target_size = int(rep_size * (int(input_size) / int(nearest_input_size)))

        # TODO: use a proper logger here
        print(f"nearest_input_size: {nearest_input_size} | root: {(target_name, rep_size)} | target_size: {target_size}")

        available_rep_funcs = [(rep_name, rep_size) for (rep_name, rep_size) in self.__model.keys() if rep_name == target_name]
        rep_func = min(available_rep_funcs, key=lambda x:abs(int(x[1]) - int(target_size)))
        _, suitable_cos, _ = self.__model[rep_func]

        # TODO: use a proper logger here
        print(f"input_size: {input_size} | rep: {rep_func} | cos: {suitable_cos}")

        return rep_func, suitable_cos

    def predict_for_benchmarked_task(self, task_id, input_size, generosity, function_exec_times):
        self.__model = self.__db.build_model(generosity)

        if task_id not in self.__task_input_map.keys():
            self.__task_input_map[task_id] = {}

        task_map = self.__task_input_map[task_id]

        if input_size in task_map.keys():
            rep_func = task_map[input_size]
            _, suitable_cos, _ = self.__model[rep_func]

            return suitable_cos

        rep_func, suitable_cos = self.__find_corresponding_model_with_exec_times(function_exec_times)
        task_map[input_size] = rep_func

        # TODO: add logic to add these data points to db for system dynamic alloc

        return suitable_cos

    def predict_for_assisted_task(self, task_id, input_size, generosity):
        self.__model = self.__db.build_model(generosity)

        if task_id not in self.__task_input_map.keys():
            self.__task_input_map[task_id] = {}

        _, suitable_cos = self.__find_corresponding_model_with_input_size(task_id, input_size)

        return suitable_cos
