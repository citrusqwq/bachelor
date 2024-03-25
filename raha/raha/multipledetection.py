import os
import detection
import dataset
import numpy as np
import random
import utilities
import evaluation
import raha


class Multipledetection:
    """
    The main class.
    """

    def __init__(self, datasets_list):
        """
        The constructor.
        """
        self.DATASETS_LIST = datasets_list
        self.ITERATION_NUM = 10
        self.DATASETS_WITHOUT_FILTERING_NUM = 2

    def get_overall_strategy_runtime(self):
        overall_runtime = 0
        for dataset_name in self.DATASETS_LIST:
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
            (
                strategies_count,
                strategies_runtime,
            ) = utilities.get_strategies_count_and_runtime(dataset_dictionary)
            print("({}) strategy runtime: {}".format(dataset_name, strategies_runtime))
            overall_runtime += strategies_runtime

        return overall_runtime

    def run_error_detection_on_datasets(self, prf_dict):
        sum_true_positive, sum_output_size, sum_actual_errors = 0, 0, 0
        app = detection.Detection()
        for index, dataset_name in enumerate(self.DATASETS_LIST):
            if index >= self.DATASETS_WITHOUT_FILTERING_NUM:
                app.STRATEGY_FILTERING = True

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

            detection_dictionary = app.run(dataset_dictionary)

            data = dataset.Dataset(dataset_dictionary)
            (
                prf_list,
                true_positive,
                output_size,
                len_actual_errors,
            ) = data.get_data_cleaning_evaluation(detection_dictionary)

            sum_true_positive += true_positive
            sum_output_size += output_size
            sum_actual_errors += len_actual_errors

            print(
                "Raha's performance on {}:\nPrecision = {:.2f}\nRecall = {:.2f}\nF1 = {:.2f}".format(
                    data.name, prf_list[0], prf_list[1], prf_list[2]
                )
            )
            print(
                "(true positive = {}, output size = {}, actual errors = {})".format(
                    true_positive, output_size, len_actual_errors
                )
            )

            prf_dict.setdefault(dataset_name, []).append(prf_list)

            if app.STRATEGY_FILTERING == False:
                app.HISTORICAL_DATASETS.append(dataset_dictionary)

        # Calculate the percision, recall and f1-score over all datasets for this iteration
        all_p = sum_true_positive / sum_output_size
        all_r = sum_true_positive / sum_actual_errors
        all_f1 = (2 * all_p * all_r) / (all_p + all_r)
        prf_dict["all"].append([all_p, all_r, all_f1])
        print(
            "Raha's performance on all datasets:\nPrecision = {:.2f}\nRecall = {:.2f}\nF1 = {:.2f}".format(
                all_p, all_r, all_f1
            )
        )
        print(
            "(sum true postive = {}, sum output size = {}, sum actual errors = {})".format(
                sum_true_positive, sum_output_size, sum_actual_errors
            )
        )

        return prf_dict


if __name__ == "__main__":
    # datasets_list = ["rayyan", "hospital", "movies_1", "beers", "flights"]
    # datasets_list = [
    #     "cou_1",
    #     "best_sellers",
    #     "cou_2",
    #     "Covid_1",
    #     "Covid_2",
    #     "imdb",
    #     "disney",
    # ]
    # datasets_no_filtering = ["beers"]
    # datasets_no_filtering = ["cou_2", "disney"]
    datasets_no_filtering = ["best_sellers", "Covid_1"]
    # datasets_filtering = ["rayyan", "flights", "hospital", "movies_1"]
    datasets_filtering = ["imdb", "disney", "cou_1", "cou_2", "Covid_2"]
    # random.shuffle(datasets_filtering)
    datasets_list = datasets_no_filtering + datasets_filtering
    print(datasets_list)

    multidetect = Multipledetection(datasets_list)

    prf_dict = {"all": []}
    for i in range(multidetect.ITERATION_NUM):
        print("\n\n >>>Iteration {}<<<<\n\n".format(i))

        prf_dict = multidetect.run_error_detection_on_datasets(prf_dict)

    # Print the average perforamce
    print(
        "\n\n-------------Average Performance over {} iterations with order:{}-------------".format(
            multidetect.ITERATION_NUM, multidetect.DATASETS_LIST
        )
    )
    print(
        "(Error detection without filtering was run on datasets: {})".format(
            multidetect.DATASETS_LIST[: multidetect.DATASETS_WITHOUT_FILTERING_NUM]
        )
    )
    print(
        "(Error detection with filtering was run on datasets: {})".format(
            multidetect.DATASETS_LIST[multidetect.DATASETS_WITHOUT_FILTERING_NUM :]
        )
    )
    for key, value in prf_dict.items():
        prf_mean_list = np.mean(value, axis=0)
        print(
            "Raha's average performance on {}:\nPrecision = {:.2f}\nRecall = {:.2f}\nF1 = {:.2f}".format(
                key, prf_mean_list[0], prf_mean_list[1], prf_mean_list[2]
            )
        )

    # Print the runtime
    strategy_runtime = multidetect.get_overall_strategy_runtime()
    print("Overall strategy runtime: {}".format(strategy_runtime))

    # Print selected strategies on filtered datasets
    for dataset_name in multidetect.DATASETS_LIST[
        multidetect.DATASETS_WITHOUT_FILTERING_NUM :
    ]:
        evaluation.print_selected_strategy(dataset_name)
