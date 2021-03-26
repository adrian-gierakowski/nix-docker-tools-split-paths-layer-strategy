from .lib import references_graph_to_igraph

# from . import lib as lib
from . import split_paths_strategy


def flatten_references_graph(references_graph, strategy):
    algo = strategy["algo"]

    if algo == "split_paths":
        layers_as_graphs = split_paths_strategy.split_graph(
            references_graph_to_igraph(references_graph),
            *strategy["args"]
        )

        return list(map(
            lambda graph: graph.vs["name"],
            layers_as_graphs
        ))
    else:
        raise Exception(f"strategy.algo {algo} not implemented!")
