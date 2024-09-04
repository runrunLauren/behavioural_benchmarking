import os
import json
from behavioural_benchmark.regression_indicators import process_regression_indicator
from behavioural_benchmark.network_indicators import process_search_trajectory_network, process_interaction_network

class MemoisedIndicators:

    def __init__(self, path, plot=False):
        # root of data files
        assert os.path.isdir(path)
        self.path = path
        self.plot = plot
        self.total_fitness_evaluations, self.total_iterations, self.infeasible_iterations, self.global_best_fitness, \
            self.solution_index = self.__parse_metadata()

        # Exploration
        self.DRoC = None  # Diversity Rate of Change
        self.ARoC_A = None  # Accuracy Rate of Change Type A
        self.ARoC_B = None  # Accuracy Rate of Change Type B

        # Exploitation
        self.CRoC = None  # Convergence Rate of Change
        self.LRoC_A = None  # Locality Rate of Change Type A
        self.LRoC_B = None  # Locality Rate of Change Type B

        # Locality in the search space
        self.ntotal = None  # Total number of nodes in the STN graph
        self.nshared = None  # Number of nodes visited more than once

        # Communication
        self.IDRoC = None  # Interaction Diversity Rate of Change
        self.ISS = None  # Influence Strength of Solution

        # Evaluation Effort
        self.ENES = None  # Average number of objective function evaluations
        self.INFEASIBLE_Percent = None  # Share of time spent in infeasible space

    def __parse_metadata(self) -> (int, float, int):
        with (open(f"{self.path}/metadata.json", "r") as f):
            data = json.load(f)
            return int(data["fitness_evaluations"]), int(data["total_iterations"]), \
                float(data["infeasible_iterations"]), float(data["global_best_fitness"]), int(data["solution_index"])

    def __process_diversity(self):
        self.DRoC, self.CRoC = process_regression_indicator(
            f"{self.path}/diversity.csv",
            x_label="iteration",
            y_label="diversity",
            slope_indices=[0, 1]
        )
        return self.DRoC, self.CRoC

    def __process_distance(self):
        self.ARoC_A, self.LRoC_A = process_regression_indicator(
            f"{self.path}/distance.csv",
            x_label="iteration",
            y_label="distance",
            slope_indices=[0, 1]
        )
        return self.ARoC_A, self.LRoC_A

    def __process_value_from_best(self):
        self.ARoC_B, self.LRoC_B = process_regression_indicator(
            f"{self.path}/value.csv",
            x_label="iteration",
            y_label="value",
            slope_indices=[0, 1]
        )
        return self.ARoC_B, self.LRoC_B

    def __process_trajectories(self):
        self.ntotal, self.nshared = process_search_trajectory_network(
            filepath=f"{self.path}/stn.csv",
            global_best_fitness=self.global_best_fitness
        )
        return self.ntotal, self.nshared

    def __process_interactions(self):
        self.IDRoC, self.ISS = process_interaction_network(
            filepath=f"{self.path}/interaction.txt",
            solution_index=self.solution_index,
            total_iterations=self.total_iterations
        )
        return self.IDRoC, self.ISS

    def get_DRoC(self) -> float:
        return self.DRoC if self.DRoC else self.__process_diversity()[0]

    def get_CRoC(self) -> float:
        return self.CRoC if self.CRoC else self.__process_diversity()[1]

    def get_ARoC_A(self) -> float:
        return self.ARoC_A if self.ARoC_A else self.__process_distance()[0]

    def get_ARoC_B(self) -> float:
        return self.ARoC_B if self.ARoC_B else self.__process_value_from_best()[0]

    def get_LRoC_A(self) -> float:
        return self.LRoC_A if self.LRoC_A else self.__process_distance()[0]

    def get_LRoC_B(self) -> float:
        return self.LRoC_B if self.LRoC_B else self.__process_value_from_best()[0]

    def get_ntotal(self):
        return self.ntotal if self.ntotal else self.__process_trajectories()[0]

    def get_nshared(self) -> float:
        return self.nshared if self.nshared else self.__process_trajectories()[1]

    def get_IDRoC(self) -> float:
        return self.IDRoC if self.IDRoC else self.__process_interactions()[0]

    def get_ISS(self) -> float:
        return self.ISS if self.ISS else self.__process_interactions()[1]

    def get_ENES(self) -> float:
        if self.ENES:
            return self.ENES
        else:
            self.ENES = self.total_fitness_evaluations / self.total_iterations
            return self.ENES

    def get_INFEASIBLE_Percent(self) -> float:
        if self.INFEASIBLE_Percent:
            return self.INFEASIBLE_Percent
        else:
            self.INFEASIBLE_Percent = self.infeasible_iterations / self.total_iterations
            return self.INFEASIBLE_Percent

