import os
import numpy
import utilities
import pickle
import raha
import scipy.spatial
import math


class Ordering:
    """
    The main class.
    """

    def __init__(self, datasets_list):
        """
        The constructor.
        """

        self.DATASETS_DICTIONARY = self.create_datasets_dictionary(datasets_list)
        self.COL_SIMILARITY_METHOD = "RAHA"
        self.TABLE_SIMILARITY_METHOD = "SUM"

    def create_datasets_dictionary(self, datasets_list):
        datasets_dict_list = []
        for dataset_name in datasets_list:
            dataset_dictionary = {
                "name": dataset_name,
                "path": os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        os.pardir,
                        "datasets",
                        dataset_name,
                        "dirty.csv",
                    )
                ),
                "clean_path": os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        os.pardir,
                        "datasets",
                        dataset_name,
                        "clean.csv",
                    )
                ),
            }
            d = raha.dataset.Dataset(dataset_dictionary)
            datasets_dict_list.append(d)
            utilities.dataset_profiler(dataset_dictionary)
        return datasets_dict_list

    def compute_weight(self):
        tuple_num = []
        col_num = []
        for dataset in self.DATASETS_DICTIONARY:
            tuple_num.append(dataset.dataframe.shape[0])
            col_num.append(dataset.dataframe.shape[1])
        tuple_sum = sum(tuple_num)
        col_sum = sum(col_num)
        tuple_ratio = [(tuple_sum - num) / tuple_sum for num in tuple_num]
        # col_ratio = [num / col_sum for num in col_num]
        # weight = numpy.multiply(tuple_ratio, col_ratio)
        return tuple_ratio

    def compute_table_similarity(self, d1_index, d2_index):
        d1 = self.DATASETS_DICTIONARY[d1_index]
        d2 = self.DATASETS_DICTIONARY[d2_index]
        d1_dp_path = os.path.join(
            os.path.dirname(d1.path),
            "raha-baran-results-" + d1.name,
            "dataset-profiling",
        )
        d2_dp_path = os.path.join(
            os.path.dirname(d2.path),
            "raha-baran-results-" + d2.name,
            "dataset-profiling",
        )

        column_sim_matrix = []
        column_sum_list = []
        for d1_column in d1.dataframe.columns.tolist():
            d1_cp = pickle.load(
                open(os.path.join(d1_dp_path, d1_column + ".dictionary"), "rb")
            )
            sim_list = []
            max = 0.0
            sum = 0
            for d2_column in d2.dataframe.columns.tolist():
                d2_cp = pickle.load(
                    open(os.path.join(d2_dp_path, d2_column + ".dictionary"), "rb")
                )

                d1_fv = []
                d2_fv = []
                for k in list(set(d1_cp["characters"]) | set(d2_cp["characters"])):
                    d1_fv.append(d1_cp["characters"][k]) if k in d1_cp[
                        "characters"
                    ] else d1_fv.append(0.0)
                    d2_fv.append(d2_cp["characters"][k]) if k in d2_cp[
                        "characters"
                    ] else d2_fv.append(0.0)
                for k in list(set(d1_cp["values"]) | set(d2_cp["values"])):
                    d1_fv.append(d1_cp["values"][k]) if k in d1_cp[
                        "values"
                    ] else d1_fv.append(0.0)
                    d2_fv.append(d2_cp["values"][k]) if k in d2_cp[
                        "values"
                    ] else d2_fv.append(0.0)
                sim = 1.0 - scipy.spatial.distance.cosine(d1_fv, d2_fv)
                sum += sim
                sim_list.append(sim)
                if sim > max:
                    max = sim

            column_sim_matrix.append(sim_list)
            column_sum_list.append(sum)
            if max == 0.0:
                print(
                    "no similar column for {}.{} comparing with {}".format(
                        d1.name, d1_column, d2.name
                    )
                )

        table_sim = math.fsum(column_sum_list)
        # print(
        #     "Column similarity matrix between dataset {} and {}".format(
        #         d1.name, d2.name
        #     )
        # )
        # print(
        #     list(map(lambda a: list(map(lambda x: "%.2f" % x, a)), column_sim_matrix))
        # )
        return table_sim

    def ordering(self):
        table_sim_matrix = numpy.zeros(
            (len(self.DATASETS_DICTIONARY), len(self.DATASETS_DICTIONARY))
        )
        for d1_index in range(len(self.DATASETS_DICTIONARY) - 1):
            for d2_index in range(d1_index + 1, len(self.DATASETS_DICTIONARY)):
                table_sim = self.compute_table_similarity(d1_index, d2_index)
                table_sim_matrix[d1_index][d2_index] = table_sim
                table_sim_matrix[d2_index][d1_index] = table_sim

        print(table_sim_matrix)
        table_sim_sum = numpy.sum(table_sim_matrix, axis=1)
        # table_sim_avg = [sum / 4 for sum in table_sim_sum]
        weight = self.compute_weight()
        print(table_sim_sum)
        print(weight)
        print(numpy.multiply(table_sim_sum, weight))


if __name__ == "__main__":
    # datasets_list = ["beers", "hospital", "rayyan", "movies_1", "flights"]
    datasets_list = [
        "disney",
        "Covid_2",
        "best_sellers",
        "cou_1",
        "cou_2",
        "Covid_1",
        "imdb",
    ]
    print(datasets_list)
    app = Ordering(datasets_list)
    app.ordering()
