import pandas as pd
from sklearn.linear_model import LinearRegression
from stnpy import stn
from swarm_interaction_network.swarm_analyzer import SwarmAnalyzer
from swarm_interaction_network.giant_component_analysis import GiantComponentDeath


def process_search_trajectory_network(filepath: str, global_best_fitness: float) -> (int, int, pd.DataFrame):
    """
    Creates a search trajectory network (STN) from a series of search trajectories. Return the number of nodes in the
    STN, and the number of nodes that are shared in the STN.

    :param filepath: the path to the csv file of trajectory information
    :param global_best_fitness: the best fitness value known in the optimisation space
    :return: the total number of nodes in the STN, and the total number of shared nodes in the STN
    """
    g = stn.StnPy(filepath)
    g.get_data(delimiter=",")
    g.create_stn(best_fit=global_best_fitness, use_best_fit_delta=True)
    return g.get_ntotal(), g.get_altered_nshared()


def process_interaction_network(filepath: str, solution_index: int, total_iterations: int) -> (float, float):
    """
    Creates an interaction network (IN) from the interaction data of the optimisation process. Returns the rate of
    change of the interaction diversity of the IN, as well as the strength of the solution node of the IN.

    :param filepath: the path to the txt file containing the interaction information
    :param solution_index: the index of the solution returned during optimisation
    :param total_iterations: the number of iterations the optimisation ran for
    :return: rate of change in interaction diversity, and the weight of the solution node
    """
    # Interaction Diversity Rate of Change
    graph = SwarmAnalyzer.create_influence_graph(filepath, window_size=1, calculate_on=1)
    number_of_components = GiantComponentDeath.low_edges_weight_removal(igraph_graph=graph, count='components')[0]
    norm_number_of_components = __normalise(number_of_components, total_iterations)
    trim_norm_number_of_components = __trim_start(norm_number_of_components, 1)

    model = LinearRegression()
    model.fit(
        trim_norm_number_of_components['x'].to_numpy().reshape(-1, 1),
        trim_norm_number_of_components['y'].to_numpy().reshape(-1, 1)
    )
    interaction_diversity_rate_of_change = model.coef_[0][0]

    # ISS
    influence_strength_of_solution = graph.strength(solution_index, weights="weight") / (2 * total_iterations)
    return float(interaction_diversity_rate_of_change), float(influence_strength_of_solution)


def __normalise(data: pd.DataFrame, t: int) -> pd.DataFrame:
    """
    Divides the weight of each node with the maximum possible weight. The maximum possible weight is twice the number of
    iterations that took place.
    """
    data['x'] /= 2 * t
    return data

def __trim_start(data: pd.DataFrame, start_value: int) -> pd.DataFrame:
    """
    Trims a dataframe by removing leading consecutive entries with values equal to the start value.
    E.g. ([1,1,1,1,2,3,4], start_value=1) -> [1,2,3,4]
    """
    start_index = data['y'][data['y'] == start_value].last_valid_index()
    return data.iloc[start_index:, :]
