import os
import json
from behavioural_benchmark.regression_indicators import process_regression_indicator
from behavioural_benchmark.network_indicators import process_search_trajectory_network, process_interaction_network
from behavioural_benchmark.mean_indicators import explore_percent, infeasible_percent

class MemoisedIndicators:

    def __init__(self, path):
        # root of data files
        assert os.path.isdir(path)
        self.path = path
        self.total_iterations, self.global_best_fitness, self.solution_index = self.__parse_metadata()

        # Diversity
        self.DRoC_A = None  # Diversity Rate of Change Type A
        self.DRoC_B = None  # Diversity Rate of Change Type B
        self.ERT_Diversity = None  # Estimated Running Time wrt Diversity
        self.Critical_Diversity = None

        # Separation
        self.SRoC_A = None  # Separation Rate of Change Type A

        # Fitness
        self.FRoC_B = None  # Fitness Rate of Change Type B
        self.Critical_Fitness = None

        # Mobility
        self.Critical_Mobility = None

        # STN
        self.ntotal = None  # Total number of nodes in the STN graph
        self.nshared = None  # Number of nodes visited more than once

        # IN
        self.MID = None  # Mean Interaction Diversity
        self.MGC = None  # Mean Giant Component
        self.SNID = None  # Solution Node in-degree

        # Others
        self.EXPLORE_Percent = None  # Exploring Percent
        self.INFEASIBLE_Percent = None  # Share of time spent in infeasible space

    def __parse_metadata(self) -> (int, float, int):
        with (open(f"{self.path}/metadata.json", "r") as f):
            data = json.load(f)
            return int(data["total_iterations"]), float(data["global_best_fitness"]), int(data["solution_index"])

    def __process_diversity(self):
        self.DRoC_A, self.DRoC_B, self.ERT_Diversity, self.Critical_Diversity = process_regression_indicator(
            f"{self.path}/diversity.csv",
            x_label="iteration",
            y_label="diversity",
            slope_indices=[0, 1]
        )
        return self.DRoC_A, self.DRoC_B, self.ERT_Diversity, self.Critical_Diversity

    def __process_separation_delta(self):
        self.SRoC_A, _, _, _ = process_regression_indicator(
            f"{self.path}/separation.csv",
            x_label="iteration",
            y_label="separation",
            slope_indices=[0, 1]
        )
        return self.SRoC_A

    def __process_fitness_delta(self):
        _, self.FRoC_B, _, self.Critical_Fitness = process_regression_indicator(
            f"{self.path}/fitness.csv",
            x_label="iteration",
            y_label="fitness",
            slope_indices=[0, 1]
        )
        return self.FRoC_B, self.Critical_Fitness

    def __process_mobility(self):
        _, _, _, self.Critical_Mobility = process_regression_indicator(
            f"{self.path}/mobility.csv",
            x_label="iteration",
            y_label="mobility",
            slope_indices=[0, 1]
        )
        return self.Critical_Mobility

    def __process_trajectories(self):
        self.ntotal, _, self.nshared, _ = process_search_trajectory_network(
            filepath=f"{self.path}/stn.csv",
            global_best_fitness=self.global_best_fitness
        )
        return self.ntotal, self.nshared

    def __process_interactions(self):
        self.MID, self.MGC, self.SNID = process_interaction_network(
            filepath=f"{self.path}/interaction_network.txt",
            solution_index=self.solution_index,
            total_iterations=self.total_iterations
        )
        return self.MID, self.MGC, self.SNID

    def get_DRoC_A(self) -> float:
        return self.DRoC_A if self.DRoC_A else self.__process_diversity()[0]

    def get_DRoC_B(self) -> float:
        return self.DRoC_B if self.DRoC_B else self.__process_diversity()[1]

    def get_ERT_Diversity(self) -> float:
        return self.ERT_Diversity if self.ERT_Diversity else self.__process_diversity()[2]

    def get_Critical_Diversity(self) -> float:
        return self.Critical_Diversity if self.Critical_Diversity else self.__process_diversity()[3]

    def get_SRoC_A(self) -> float:
        return self.SRoC_A if self.SRoC_A else self.__process_separation_delta()[0]

    def get_FRoC_B(self) -> float:
        return self.FRoC_B if self.FRoC_B else self.__process_fitness_delta()[1]

    def get_Critical_Fitness(self) -> float:
        return self.Critical_Fitness if self.Critical_Fitness else self.__process_fitness_delta()[3]

    def get_Critical_Mobility(self) -> float:
        return self.Critical_Mobility if self.Critical_Mobility else self.__process_mobility()[3]

    def get_ntotal(self):
        return self.ntotal if self.ntotal else self.__process_trajectories()[0]

    def get_nshared(self) -> float:
        return self.nshared if self.nshared else self.__process_trajectories()[2]

    def get_MID(self) -> float:
        return self.MID if self.MID else self.__process_interactions()[0]

    def get_MGC(self) -> float:
        return self.MGC if self.MGC else self.__process_interactions()[1]

    def get_SNID(self) -> float:
        return self.SNID if self.SNID else self.__process_interactions()[2]

    def get_EXPLORE_Percent(self) -> float:
        if self.EXPLORE_Percent:
            return self.EXPLORE_Percent
        else:
            self.EXPLORE_Percent = explore_percent(filepath=f"{self.path}/diversity.csv")
            return self.EXPLORE_Percent

    def get_INFEASIBLE_Percent(self) -> float:
        if self.INFEASIBLE_Percent:
            return self.INFEASIBLE_Percent
        else:
            self.INFEASIBLE_Percent = infeasible_percent(filepath=f"{self.path}/f_percent.csv")
            return self.INFEASIBLE_Percent

