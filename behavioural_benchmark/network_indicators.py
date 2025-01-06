import numpy as np
from behavioural_benchmark.stn import StnPy
from swarm_interaction_network.swarm_analyzer import SwarmAnalyzer
from swarm_interaction_network.giant_component_analysis import GiantComponentDeath


def process_search_trajectory_network(filepath: str, global_best_fitness: float) -> (int, int):
    """
    Creates a search trajectory network (STN) from a series of search trajectories. Return the number of nodes in the
    STN, and the number of nodes that are shared in the STN.

    :param filepath: the path to the csv file of trajectory information
    :param global_best_fitness: the best fitness value known in the optimisation space
    :return: the total number of nodes in the STN, the total number of shared nodes in the STN
    """
    g = StnPy(filepath)
    g.get_data(delimiter=",")
    g.create_stn(best_fit=global_best_fitness, use_best_fit_delta=True)
    return g.get_ntotal(), g.get_altered_nshared()


def process_interaction_network(filepath: str, solution_index: int, total_iterations: int) -> (float, float, float):
    """
    Creates an interaction network (IN) from the interaction data of the optimisation process. Returns the mean
    interaction diversity of the IN, the mean giant component size of the IN, as well as the in-degree of the solution
    node of the IN.

    :param filepath: the path to the txt file containing the interaction information
    :param solution_index: the index of the solution returned during optimisation
    :param total_iterations: the number of iterations the optimisation ran for
    :return: mean interaction diversity, mean giant component, and the in-degree of the solution node
    """
    graph = SwarmAnalyzer.create_influence_graph(filepath, window_size=1, calculate_on=1)
    graph.es['weight'] = [w / (2 * total_iterations) for w in graph.es['weight']]

    # Interaction Diversity
    number_of_components = GiantComponentDeath.low_edges_weight_removal(igraph_graph=graph, count='components')[0]
    mean_id = np.mean(number_of_components['y'])

    # Mean Giant Component
    size_of_largest_subgraph = GiantComponentDeath.low_edges_weight_removal(igraph_graph=graph, count='size')[0]
    mean_gc = np.mean(size_of_largest_subgraph['y'])

    # solution node in degree
    snid = graph.strength(solution_index, weights="weight")

    return float(mean_id), float(mean_gc), float(snid)
