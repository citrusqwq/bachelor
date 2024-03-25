import os
import pickle
from operator import itemgetter


def print_dataset_profiling(dataset_name):
    ndp_folder_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            "datasets",
            dataset_name,
            "raha-baran-results-" + dataset_name,
            "dataset-profiling",
        )
    )
    ncp = pickle.load(
        open(os.path.join(ndp_folder_path, "ounces" + ".dictionary"), "rb")
    )
    print(ncp)


def get_evaluation_profiling(dataset_name):
    ep_folder_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            "datasets",
            dataset_name,
            "raha-baran-results-" + dataset_name,
            "evaluation-profiling",
        )
    )

    evaluation_dict = {}
    for column_dict in os.listdir(ep_folder_path):
        evaluation_dict[column_dict] = pickle.load(
            open(os.path.join(ep_folder_path, column_dict), "rb")
        )

    return evaluation_dict
    # print(len(evaluation_dict["flight.dictionary"]))
    # print(evaluation_dict["flight.dictionary"])


def print_selected_strategy(dataset_name):
    sp_folder_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            "datasets",
            dataset_name,
            "raha-baran-results-" + dataset_name,
            "selected-strategy",
        )
    )

    strategy_profiles_list = [
        pickle.load(open(os.path.join(sp_folder_path, strategy_file), "rb"))
        for strategy_file in os.listdir(sp_folder_path)
    ]

    column_strategy_dict = {}
    for strategy_profile in strategy_profiles_list:
        selected_strategy = [
            strategy_profile["name"],
            strategy_profile["historical_column"],
            strategy_profile["score"],
        ]
        column_strategy_dict.setdefault(strategy_profile["new_column"], []).append(
            selected_strategy
        )

    evaluation_dict = get_evaluation_profiling(dataset_name)

    for key, value in column_strategy_dict.items():
        print("\nOn new column {}, {} strategies are applied:".format(key, len(value)))
        dict_name = key.split(".")[1] + ".dictionary"
        col_eval_dict = evaluation_dict[dict_name]
        for strategy in value:
            print(
                "{}, hc: {}, sf_score: {:.3f}, prf:{}".format(
                    strategy[0],
                    strategy[1],
                    strategy[2],
                    [round(elem, 3) for elem in col_eval_dict[strategy[0]]],
                )
            )


def print_strategy_profile(dataset_name):
    sp_folder_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            "datasets",
            dataset_name,
            "raha-baran-results-" + dataset_name,
            "strategy-profiling",
        )
    )

    strategy_profiles_list = [
        pickle.load(open(os.path.join(sp_folder_path, strategy_file), "rb"))
        for strategy_file in os.listdir(sp_folder_path)
    ]

    print(strategy_profiles_list)


if __name__ == "__main__":
    dataset_name = "beers"

    # get_evaluation_profiling(dataset_name)
    print_selected_strategy(dataset_name)
