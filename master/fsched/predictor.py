from config import Config

from db.csv import CSVAdapter


class CachePredictor:
    # FIXME: pass config as argument to constructor instead of reading directly from Config
    def __init__(self):
        # FIXME: reading csv file for now will switch to db later
        self.__db = CSVAdapter()

    @staticmethod
    def __run_mse(model_exec_times, function_exec_times):
        return sum((yt - yp) ** 2 for yt, yp in zip(model_exec_times, function_exec_times))

    def predict_for_function(self, task_id, generosity, function_exec_times):
        # _ = task_id
        model = self.__db.build_model(generosity)

        target = (None, None, None)
        for (key, val) in model.items():
            model_exec_times, x_model, y_model = val

            reg_exec_times = self.__db.fit_regression(function_exec_times)

            min_mse, _, _ = target
            mse = self.__run_mse(model_exec_times, reg_exec_times)

            if min_mse is None or mse < min_mse:
                target = (mse, x_model, y_model)

        _, suitable_cos, pred_exec_time = target

        return (suitable_cos, pred_exec_time)
