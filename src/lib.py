from pathlib import Path
import igraph as igraph
import itertools as itertools
import json as json
import os as os

DEBUG = os.environ.get("DEBUG", False) == "True"


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def unnest_iterable(xs):
    return itertools.chain.from_iterable(xs)


def flat_map(f, xs):
    ys = []
    for x in xs:
        ys.extend(f(x))
    return ys


def load_json(file_path):
    with open(file_path) as f:
        return json.load(f)


def egdes_for_reference_graph_node(reference_graph_node):
    source = reference_graph_node["path"]
    return map(
        lambda x: {"source": source, "target": x},
        filter(
            # references might contain source
            lambda x: x != source,
            reference_graph_node["references"]
        )
    )


def vertex_from_reference_graph_node(reference_graph_node):
    return {
        "name": reference_graph_node["path"],
        "closureSize": reference_graph_node["closureSize"],
        "narSize": reference_graph_node["narSize"],
    }


def references_graph_to_igraph(references_graph):
    """
    Converts result of exportReferencesGraph into an igraph directed graph.
    Uses paths as igraph node names, and sets closureSize and narSize as
    properties of igraph nodes.
    """
    return igraph.Graph.DictList(
        map(vertex_from_reference_graph_node, references_graph),
        unnest_iterable(map(egdes_for_reference_graph_node, references_graph)),
        directed=True
    )


def load_closure_graph(file_path):
    return references_graph_to_igraph(load_json(file_path))


def path_relative_to_file(file_path_from, file_path):
    dir_path = Path(file_path_from).parent
    return dir_path / file_path


def is_None(x):
    return x is None
