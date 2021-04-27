from toolz import curried as tlz

from .lib import references_graph_to_igraph, flatten
from .pipe import pipe

MAX_LAYERS = 127


def create_list_of_lists_of_strings(deeply_nested_lists_or_dicts_of_graphs):
    list_or_graphs = flatten(deeply_nested_lists_or_dicts_of_graphs)

    return list(tlz.map(
        lambda g: g.vs["name"],
        list_or_graphs
    ))


def flatten_references_graph(references_graph, pipeline):
    igraph_graph = references_graph_to_igraph(references_graph)

    return create_list_of_lists_of_strings(pipe(
        pipeline,
        igraph_graph
    ))
