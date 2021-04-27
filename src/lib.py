from collections.abc import Iterable
from pathlib import Path
from toolz import curried as tlz
from toolz import curry
import igraph as igraph
import itertools as itertools
import json as json
import os as os
import re as re

DEBUG = os.environ.get("DEBUG", False) == "True"
DEBUG_PLOT = os.environ.get("DEBUG_PLOT", False) == "True"


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def debug_plot(g, **kwargs):
    if not DEBUG_PLOT:
        return

    vertex_label = [
        # remove /nix/store/HASH- prefix from labels
        re.split("^/nix/store/[a-z0-9]{32}-", name)[-1]
        for name in g.vs["name"]
    ]

    igraph.plot(
        g,
        vertex_label=vertex_label,
        **(tlz.merge(
            {
                "bbox": (3840, 2160),
                "margin": 100,
                "vertex_label_dist": -5,
                "edge_color": "orange",
                "vertex_label_size": 45
            },
            kwargs
        )),
    )


def debug_plot_with_highligth(g, vs, layout):
    debug_plot(
        g,
        layout=layout,
        # layout=Layout(new_coords),
        vertex_color=[
            "green" if v.index in vs else "red"
            for v in g.vs
        ]
    )


@curry
def pick_keys(keys, d):
    return {
        key: d[key] for key in keys if key in d
    }


def unnest_iterable(xs):
    return itertools.chain.from_iterable(xs)


def load_json(file_path):
    with open(file_path) as f:
        return json.load(f)


@curry
def sorted_by(key, xs):
    return sorted(xs, key=lambda x: x[key])


@curry
def find_vertex_by_name_or_none(graph, name):
    try:
        # NOTE: find by name is constant time.
        return graph.vs.find(name)
    # This will be thrown if vertex with given name is not found.
    except ValueError:
        return None


def subcomponent_multi(graph, vertices, mode="out"):
    """Return concatenated subcomponents generated by the given list of
    vertices.
    """
    return tlz.mapcat(
        lambda vertex: graph.subcomponent(vertex, mode=mode),
        vertices
    )


@curry
def egdes_for_reference_graph_node(path_to_size_dict, reference_graph_node):
    source = reference_graph_node["path"]
    return map(
        lambda x: {"source": source, "target": x},
        sorted(
            filter(
                # references might contain source
                lambda x: x != source,
                reference_graph_node["references"]
            ),
            key=lambda x: 1 * path_to_size_dict[x]
        )
    )


reference_graph_node_keys_to_keep = [
    "closureSize",
    "narSize"
]

pick_reference_graph_node_keys = pick_keys(reference_graph_node_keys_to_keep)


def vertex_from_reference_graph_node(reference_graph_node):
    return tlz.merge(
        {"name": reference_graph_node["path"]},
        pick_reference_graph_node_keys(reference_graph_node)
    )


def references_graph_to_igraph(references_graph):
    """
    Converts result of exportReferencesGraph into an igraph directed graph.
    Uses paths as igraph node names, and sets closureSize and narSize as
    properties of igraph nodes.
    """
    debug('references_graph', references_graph)
    references_graph = sorted(references_graph, key=lambda x: 1 * x["narSize"])

    path_to_size_dict = {
        node["path"]: node["narSize"] for node in references_graph
    }

    debug('path_to_size_dict', path_to_size_dict)

    return igraph.Graph.DictList(
        map(vertex_from_reference_graph_node, references_graph),
        unnest_iterable(map(
            egdes_for_reference_graph_node(path_to_size_dict),
            references_graph
        )),
        directed=True
    )


@curry
def graph_vertex_index_to_name(graph, index):
    return graph.vs[index]["name"]


def igraph_to_reference_graph(igraph_instance):
    return [
        tlz.merge(
            {
                "path": v["name"],
                "references": list(map(
                    graph_vertex_index_to_name(igraph_instance),
                    igraph_instance.successors(v.index)
                ))
            },
            pick_reference_graph_node_keys(v.attributes())
        )
        for v in igraph_instance.vs
    ]


def load_closure_graph(file_path):
    return references_graph_to_igraph(load_json(file_path))


def path_relative_to_file(file_path_from, file_path):
    dir_path = Path(file_path_from).parent
    return dir_path / file_path


def is_None(x):
    return x is None


def not_None(x):
    return x is not None


def print_layers(layers):
    debug("\n::::LAYERS:::::")
    for index, layer in enumerate(layers):
        debug("")
        debug("layer index:", index)
        debug("[")
        for v in layer.vs["name"]:
            debug("  ", v)
        debug("]")


def print_vs(graph):
    for v in graph.vs:
        debug(v)


def directed_graph(edges, vertices=None, vertex_attrs=[]):
    graph = igraph.Graph.TupleList(edges, directed=True)

    # Add detached vertices (without edges) if any.
    if vertices is not None:
        graph = graph + vertices

    # Add vertex attributes if any.
    for (name, attrs_dict) in vertex_attrs:
        vertex = graph.vs.find(name)

        for (k, v) in attrs_dict.items():
            vertex[k] = v

    return graph


def empty_directed_graph():
    return directed_graph([])


def graph_is_empty(graph):
    return len(graph.vs) == 0


def pick_attrs(attrs, x):
    return {attr: getattr(x, attr) for attr in attrs}


def merge_graphs(graphs):
    return tlz.reduce(lambda acc, g: acc + g, graphs)


# Functions below can be used in user defined pipeline (see pipe.py).
# All functions need to be curried, and the user needs to be able to
# provide values for all arguments apart from the last one from nix code.
@curry
def over(prop_name, func, dictionary):
    value = dictionary[prop_name]
    return tlz.assoc(dictionary, prop_name, func(value))


# One argument functions also need to be curried to simplify processing of the
# pipeline.
@curry
def flatten(xs):
    xs = xs.values() if isinstance(xs, dict) else xs
    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


@curry
def split_every(count, graph):
    vs = graph.vs
    return [
        graph.induced_subgraph(vs[x:x + count])
        for x in range(0, len(vs), count)
    ]


@curry
def limit_layers(max_count, graphs):
    assert max_count > 1, "max count needs to > 1"

    graphs_iterator = iter(graphs)

    return tlz.concat([
        tlz.take(max_count - 1, graphs_iterator),
        # Merges all graphs remaining in the iterator, after initial
        # max_count - 1 have been taken.
        (lambda: (yield merge_graphs(graphs_iterator)))()
    ])
