import pandas as pd
from sklearn.linear_model import LinearRegression
import igraph
import numpy as np
from stnpy import stn
from swarm_interaction_network.swarm_analyzer import SwarmAnalyzer
from swarm_interaction_network.giant_component_analysis import GiantComponentDeath


def process_search_trajectory_network(filepath: str, global_best_fitness: float) -> (int, int):
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


def process_interaction_network(filepath: str, best_index: int, max_iterations: int) -> (float, float):
    """

    :param filepath: the path to the txt file containing the interaction information
    :param best_index:
    :param max_iterations:
    :return:
    """
    # this graph is actually just an igraph graph
    graph: igraph.Graph = SwarmAnalyzer.create_influence_graph(filepath, window_size=1, calculate_on=1)

    # Interaction Diversity Rate of Change
    components_count = _normalise_(
        GiantComponentDeath.low_edges_weight_removal(igraph_graph=graph, count='components')[0],
        max_iterations
    )
    trimmed_components_count = _trim_start_(components_count, 1)
    model = LinearRegression()
    model.fit(
        np.array(trimmed_components_count['x']).reshape(-1, 1),
        np.array(trimmed_components_count['y']).reshape(-1, 1)
    )
    interaction_diversity_rate_of_change = model.coef_[0][0]

    # ISS
    influence_strength_of_solution = graph.strength(best_index, weights="weight") / (2 * max_iterations)
    return interaction_diversity_rate_of_change, influence_strength_of_solution


def _normalise_(data: pd.DataFrame, t: int) -> pd.DataFrame:
    """
    Divides the weight of each node with the maximum possible weight. The maximum possible weight is twice the number of
    iterations that took place.
    """
    data['x'] = data['x'].apply(lambda x: x / (2 * t))
    return data

def _trim_start_(data: pd.DataFrame, start_value: int) -> pd.DataFrame:
    """
    Trims a dataframe by removing leading consecutive entries with values equal to the start value.
    E.g. ([1,1,1,1,2,3,4], start_value=1) -> [1,2,3,4]
    """
    start_index = data['y'][data['y'] == start_value].last_valid_index()
    return data.iloc[start_index:, :]