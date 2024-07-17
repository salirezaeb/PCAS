import numpy as np
import pandas as pd

from scipy.optimize import curve_fit, fsolve, minimize_scalar

from config import Config


class CSVAdapter:
    # FIXME: pass config as argument to constructor instead of reading directly from Config
    def __init__(self):
        self.__cos_count = Config.COS_COUNT
        self.__df = pd.read_csv(Config.DB_CSV_PATH)
        self.__function_list = [
            "page_rank.py",
            "matrix_multi.py",
            "graph_mst.py",
            "graph_bfs.py",
            "image_recognition.py",
            "image_resize.py",
            "video_processing.py",
        ]

    @staticmethod
    def __asymptotic_func(x, a, b):
        return a + (b / (1 + (x - 1) ** 0.5))

    @staticmethod
    def __asymptotic_derivative(x, b):
        return -b * 0.5 * (x - 1) ** (-0.5) / (1 + (x - 1) ** 0.5) ** 2

    @staticmethod
    def __find_x_for_slope(S, a, b):
        def equation(x):
            return CSVAdapter.__asymptotic_derivative(x, b) - S

        x_initial_guess = 1.1
        x_solution = fsolve(equation, x_initial_guess)
        return x_solution[0]

    # FIXME: this is shit code and needs to be refactored
    # FIXME: this should be done periodically not on api call
    def build_model(self, generosity):
        model = {}

        for name in self.__function_list:
            df_target = self.__df[self.__df["name"] == name]

            unique_input_sizes = df_target["input_size"].unique()
            unique_input_sizes.sort()

            for size in unique_input_sizes:
                df_size = df_target[df_target["input_size"] == size]

                x_data = df_size["cos"]
                y_data = df_size["exec_time"]

                if y_data.empty:
                    continue

                params, _ = curve_fit(CSVAdapter.__asymptotic_func, x_data, y_data, p0=[1, 1])

                x_fit = np.linspace(x_data.min(), x_data.max(), 100)
                y_fit = CSVAdapter.__asymptotic_func(x_fit, *params)

                x_slope = CSVAdapter.__find_x_for_slope(generosity, params[0], params[1])

                x_best = min(int(np.ceil(x_slope)), 10)
                y_best = CSVAdapter.__asymptotic_func(x_best, *params)

                model_exec_times = [CSVAdapter.__asymptotic_func(cos, *params) for cos in range(1, self.__cos_count)]

                model[(name, size)] = (model_exec_times, x_best, y_best)

        return model
