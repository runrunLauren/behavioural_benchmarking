import numpy as np
import pandas as pd
import math
import networkx as nx
from statistics import mean


class StnPy:
    """
    StnPY provides a minimal implementation of STN technology, as seen in "Gabriela Ochoa, Katherine Malan, Christian
    Blum (2021) Search trajectory networks: A tool for analysing and visualising the behaviour of metaheuristics,
    Applied Soft Computing, Elsevier. https://doi.org/10.1016/j.asoc.2021.107492."

    The implementation follows the directions of the paper cited above, as well as the scripts written in R and hosted
    by the authors on https://github.com/gabro8a/STNs.

    The full functionality as provided by the authors is not replicated here, rather only the functionality of creating
    STNs for a single algorithm and generating those STN-based metrics are supported. For the merging of STNs, and the
    creation of merged STN-metrics, please see the authors work.

    As this implementation follows the directions of the paper cited above, the input is structured in a very specific
    way. Please see below.

    Example of an STN input file as per the original paper:

    Run,Fitness1,Solution1,Fitness2,Solution2
    1,5.0,006200,5.0,005000
    1,3.0,003200,1.0,002500

    The "Solution1" and "Solution2" text is a representation of the position vector. In the paper, these representations
     are called `locations` in the search space, and are meant to be larger than a unique point in the multidimensional
     space. There are many ways this can be done, and it is left to the user. In the example above, a continuous domain
     is represented by the concatenation of the percentile of the given dimension of the position vector.

    See the following example:

    For a problem of dimension = 3, and each dimension a domain of 0 to 1.
    [0.058, 0.0]

    To convert 0.06 to a percentile of 0 and 1, divide the domain into 100 equal sections. That is 0.0 <= x < 0.01 is the
    0th percentile. Then 0.01 <= x < 0.02 is the 1st percentile. And so forth. Each dimension in the position vector can
    be mapped to an integer between 0 and 99 this way. Furthermore, by zero-padding the integers, each dimension is
    represented by a two-digit

    0.0 <= 0.008 < 0.01 is the 0th percentile.
    0.62 <= 0.6289 < 0.63 is the 62nd percentile.
    0.00 <= 0.003 < 0.01 is the 0th percentile.

    Then the representation of  [0.088, 0.6289, 0.003] becomes 006200.s
    """

    def __init__(self, filename):
        # metadata
        self.filename = filename
        self.nruns = None
        self.data = None
        # graph and associated
        self.index_map = None
        self.graph = None
        # metric metadata
        self.best_vertexes = None
        # metrics
        self.ntotal = None
        self.etotal = None
        self.nbest = None
        self.nend = None
        self.components = None
        self.best_strength = None
        self.plength = None
        self.npaths = None
        self.nshared = None

    def __map_positions(self, positions):
        """
        Map the long position identifier to a shorter, integer identifier
        """
        next_id = 0
        position_id_map = {}
        for position in positions:
            if position not in position_id_map:
                position_id_map[position] = next_id
                next_id += 1
        return position_id_map

    def __metric_exists(self, metric):
        if self.graph is None:
            raise Exception("Graph not initialized. Run `create_stn` first.")
        if metric is None:
            return False
        return True

    def get_ntotal(self):
        if not self.__metric_exists(self.ntotal):
            self.ntotal = len(self.graph.nodes)
        return self.ntotal

    def get_etotal(self):
        if not self.__metric_exists(self.etotal):
            self.etotal = len(self.graph.edges)
        return self.etotal

    def get_nbest(self):
        if not self.__metric_exists(self.nbest):
            self.best_vertexes = [node for node in self.graph.nodes if self.graph.nodes[node]["type"] == "best"]
            self.nbest = len(self.best_vertexes)
            if self.nbest > 0:
                self.best_strength = \
                    (sum([self.graph.in_degree(n, weight="weight") for n in self.best_vertexes]) / self.nruns)
            else:
                self.best_strength = 0
        return self.nbest

    def get_nend(self):
        if not self.__metric_exists(self.nend):
            end_vertexes = [node for node in self.graph.nodes if self.graph.nodes[node]["type"] == "end"]
            self.nend = len(end_vertexes)
        return self.nend

    def get_components(self):
        if not self.__metric_exists(self.components):
            self.components = nx.number_weakly_connected_components(self.graph)
        return self.components

    def get_best_strength(self):
        self.get_nbest()
        return self.best_strength

    def get_npaths(self):
        self.get_nbest()
        if not self.__metric_exists(self.npaths):
            start_vertexes = [node for node in self.graph.nodes if self.graph.nodes[node]["type"] == "start"]
            if self.nbest > 0:
                paths = []
                for sn in start_vertexes:
                    for bn in self.best_vertexes:
                        try:
                            paths += nx.all_shortest_paths(self.graph, sn, target=bn)
                        except Exception as _:
                            # no path from source to target
                            continue
                paths_len = [len(path) for path in paths]
                self.npaths = len(paths)
                self.plength = -1
                if self.npaths > 0:
                    self.plength = mean(paths_len)
            else:
                self.npaths = 0
                self.plength = -1
        return self.npaths

    def get_plength(self):
        self.get_npaths()
        return self.plength

    def get_altered_nshared(self):
        """
        this nshared is different from the one described in the paper. In the paper, nshared is only valid if more than
        one algorithm is being combined in one STN. However, the paper defines nshared to be the number of locations
        that are attractive to more than one algorithm, which I feel generalises just as well to the number of locations
        that were attractive to more than one run.

        Therefore, this generalises to number of nodes that have been visited by more than one run.

        :return: nshared as described above
        """
        if not self.__metric_exists(self.nshared):
            self.nshared = len([n for n, l in nx.get_node_attributes(self.graph, name="run").items() if len(l) > 1])
        return self.nshared

    def get_data(self, delimiter, run_numbers=None, dtype_dict=None):
        if dtype_dict is None:
            dtype_dict = {"Run": int, "Fitness1": float, "Solution1": float, "Fitness2": float, "Solution2": float}
        try:
            df = pd.read_csv(self.filename, delimiter=delimiter, dtype=dtype_dict, engine='c', memory_map=True)
            if run_numbers is not None:
                df = df[df["Run"].isin(run_numbers)]
            self.nruns = df["Run"].nunique()
            self.data = df
            return
        except Exception as e:
            raise Exception(f"Input file '{self.filename}' could not be read with delimiter '{delimiter}', due to:\n\""
                            f"{e}\"")

    def create_stn(self, best_fit=None, use_best_fit_delta=False, best_fit_delta=None):
        if self.data is None:
            raise Exception("No data available. Call `get_data` first.")

        df = self.data  # just for a nice alias

        # Preprocess the info by mapping the large positions to position IDs
        nodes_and_values = pd.DataFrame(np.concatenate([df[['Solution1', 'Fitness1']].values,
                                                        df[['Solution2', 'Fitness2']].values]),
                                        columns=['position', 'fitness'])
        nodes_and_values.drop_duplicates(inplace=True)
        position_map = self.__map_positions(nodes_and_values['position'].to_list())
        self.index_map = dict((v, k) for k, v in position_map.items())
        df['Solution1'] = df['Solution1'].map(lambda x: position_map[x])
        df['Solution2'] = df['Solution2'].map(lambda x: position_map[x])

        # determine the best fitness (or what is close enough to be called best)
        if best_fit is None:
            best_fit = min(nodes_and_values['fitness'])
        if use_best_fit_delta:
            worst_fit = max(nodes_and_values['fitness'].replace([np.inf, -np.inf], np.nan))
            if best_fit_delta is None:
                best_fit_delta = math.log10(abs(worst_fit) + 1) / 100
        else:
            best_fit_delta = 0.0
        best_ids = list(df.query("abs(Fitness2 - @best_fit) <= @best_fit_delta")["Solution2"].unique())

        # Create the graphs per run and merge them with the global graph
        # We do this so that we can grab the start and end nodes of each run
        self.graph = nx.MultiDiGraph()
        start_nodes = []
        end_nodes = []
        for run in list(df["Run"].unique()):
            df_run = df[df["Run"] == run]

            g = nx.from_pandas_edgelist(
                df_run,
                source='Solution1',
                target='Solution2',
                create_using=nx.MultiDiGraph
            )
            for node in g.nodes:
                if g.out_degree(node) == 0:
                    end_nodes.append(node)
                if g.in_degree(node) == 0:
                    start_nodes.append(node)

            # put run attributes together
            nx.set_node_attributes(g, values=[run], name="run")
            run_values = nx.get_node_attributes(g, name="run")
            existing_values = nx.get_node_attributes(self.graph, name="run")
            for node_id, run_list in run_values.items():
                if node_id not in existing_values:
                    existing_values[node_id] = run_list
                else:
                    expanded_list = run_list + existing_values[node_id]
                    existing_values[node_id] = expanded_list
            self.graph.add_nodes_from(g.nodes)
            nx.set_node_attributes(self.graph, values=existing_values, name="run")

            # `add_edges_from` doesn't honour multi-edges
            for source, target, key in g.edges:
                if self.graph.has_edge(source, target, key):
                    weight = self.graph.edges[source, target, key]['weight']
                    self.graph.edges[source, target, key]['weight'] = weight + 1
                else:
                    self.graph.add_edge(source, target, weight=1)

        # assign values
        for node in self.graph.nodes:
            self.graph.nodes[node]["type"] = "medium"
            if node in end_nodes:
                self.graph.nodes[node]["type"] = "end"
            if node in start_nodes:
                self.graph.nodes[node]["type"] = "start"
            if node in best_ids:
                self.graph.nodes[node]["type"] = "best"
