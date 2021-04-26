import os as os

from toolz import curry
from toolz import curried as tlz

import igraph as igraph
import itertools as itertools
import re as re

from functools import reduce

from .lib import (
    debug,
    unnest_iterable,
    is_None,
    find_vertex_by_name_or_none,
    subcomponent_multi
)

DEBUG_PLOT = os.environ.get("DEBUG_PLOT", False) == "True"

added_root_name = "__root__"


def add_root(graph):
    """Add single root to the graph connected to all existing roots.

    If graph has only one root, return the graph unchanged and the name
    of the root vertex.

    Otherwise return a modified graph (copy) and a name of the add root vertex.
    """
    global added_root_name

    roots = graph.vs.select(lambda v: len(graph.predecessors(v)) == 0)
    root_names = roots["name"]
    if len(root_names) == 1:
        return graph, root_names[0]
    else:
        edges = [(added_root_name, v) for v in root_names]
        graph_with_root = graph + added_root_name + edges
        return graph_with_root, added_root_name


def get_children_of(graph, vertex_names):
    return unnest_iterable(map(
        graph.successors,
        itertools.filterfalse(
            is_None,
            map(
                find_vertex_by_name_or_none(graph),
                vertex_names
            )
        )
    ))


@curry
def split_path_spec_to_indices(graph, split_path_spec):
    debug("split_path_spec", split_path_spec)
    if isinstance(split_path_spec, dict):
        if "children_of" in split_path_spec:
            children_of = split_path_spec["children_of"]

            return get_children_of(graph, (
                [children_of]
                if isinstance(children_of, str)
                else children_of
            ))
        else:
            raise Exception(
                "Unexpected split path spec: dict with invalid keys."
                "Valid: [\"children_of\"]"
            )
    else:
        vertex = find_vertex_by_name_or_none(graph)(split_path_spec)
        return [] if is_None(vertex) else [vertex.index]


def split_below(graph_in, split_paths):
    debug("____")
    debug("split_paths:", split_paths)
    debug("graph_in:", graph_in)

    # Convert list of split_paths into list of vertex indices. Ignores
    # split_paths which don"t match any vertices in the graph.
    # All edges pointing at the indices will be deleted from the graph.
    split_path_indices = list(unnest_iterable(map(
        split_path_spec_to_indices(graph_in),
        split_paths
    )))

    debug("split_path_indices:", split_path_indices)

    # Short circuit if there is nothing to do (split_paths didn"t match any
    # vertices in the graph).
    if len(split_path_indices) == 0:
        return None

    # If graph has multiple roots, add a single one connecting all existing
    # roots to make it easy to split the graph into 2 sets of vertices after
    # deleting edges pointing at split_path_indices.
    graph, root_name = add_root(graph_in)

    debug("root_name", root_name)

    if find_vertex_by_name_or_none(graph)(
            root_name).index in split_path_indices:
        return {"main": graph}

    # Copy graph if add_root has not already created a copy, since we are
    # going to mutate the graph and don"t want to mutate a function argument.
    graph = graph if graph is not graph_in else graph.copy()

    if DEBUG_PLOT:
        layout = graph.layout()
        debug_plot(graph, layout=layout)

    # Get incidences of all vertices which can be reached split_path_indices
    # (including split_path_indices). This is a set of all split_paths and their
    # dependencies.
    split_off_vertex_indices = frozenset(
        subcomponent_multi(graph, split_path_indices, mode="in"))
    debug("split_off_vertex_indices", split_off_vertex_indices)

    # Delete edges which point at any of the vertices in split_path_indices.
    graph.delete_edges(_source_in=split_path_indices)

    if DEBUG_PLOT:
        debug_plot(graph, layout=layout)

    # Get incidences of all vertices which can be reached from the root. Since
    # edges pointing at split_path_indices have been deleted, none of the
    # split_path_indices will be included. Dependencies of rest_with_common will
    # only be included if they can be reached from any vertex which is itself
    # not in split_off_vertex_indices.
    main_with_common = frozenset(graph.subcomponent(root_name, mode="out"))
    debug("main_with_common", main_with_common)

    # Get a set of all dependencies common to split_path_indices and the rest
    # of the graph.
    common = split_off_vertex_indices.intersection(main_with_common)
    debug("common", common)

    # Get a set of vertices which cannot be reached from split_path_indices.
    rest_without_common = main_with_common.difference(common)
    debug("rest_without_common", rest_without_common)

    # Get a set of split_path_indices and their dependencies which cannot be
    # reached from the rest of the graph.
    split_off_without_common = split_off_vertex_indices.difference(common)
    debug("split_off_without_common", split_off_without_common)

    if DEBUG_PLOT:
        def choose_color(index):
            if (index in split_off_without_common):
                return "green"
            elif (index in rest_without_common):
                return "red"
            else:
                return "purple"

        vertex_color = [choose_color(v.index) for v in graph.vs]

        debug_plot(
            graph,
            layout=layout,
            vertex_color=vertex_color
        )

    # Return subgraphs based on calculated sets of vertices.
    return {
        # Dependencies of split paths which can be reached from the rest of the
        # graph.
        "common": graph.induced_subgraph(common),
        # Rest of the graph (without dependencies common with split paths).
        "rest": graph.induced_subgraph(rest_without_common),
        # Split paths and their deps (unreachable from rest of the graph).
        "main": graph.induced_subgraph(split_off_without_common)
    }


def split(graph_in, split_paths):
    debug("____")
    debug("split_paths:", split_paths)
    debug("graph_in:", graph_in)

    # Convert list of split_paths into list of vertex indices. Ignores
    # split_paths which don"t match any vertices in the graph.
    # All edges pointing at the indices will be deleted from the graph.
    split_path_indices = list(unnest_iterable(map(
        split_path_spec_to_indices(graph_in),
        split_paths
    )))

    debug("split_path_indices:", split_path_indices)

    # Short circuit if there is nothing to do (split_paths didn"t match any
    # vertices in the graph).
    if len(split_path_indices) == 0:
        return None

    # If graph has multiple roots, add a single one connecting all existing
    # roots to make it easy to split the graph into 2 sets of vertices after
    # deleting edges pointing at split_path_indices.
    graph, root_name = add_root(graph_in)

    debug("root_name", root_name)

    if find_vertex_by_name_or_none(graph)(
            root_name).index in split_path_indices:
        return {"main": graph}

    # Copy graph if add_root has not already created a copy, since we are
    # going to mutate the graph and don"t want to mutate a function argument.
    graph = graph if graph is not graph_in else graph.copy()

    if DEBUG_PLOT:
        layout = graph.layout('tree')
        debug_plot(graph, layout=layout)

    # Get incidences of all vertices which can be reached split_path_indices
    # (including split_path_indices). This is a set of all split_paths and their
    # dependencies.
    split_off_vertex_indices = frozenset(
        subcomponent_multi(graph, split_path_indices))
    debug("split_off_vertex_indices", split_off_vertex_indices)

    # Delete edges which point at any of the vertices in split_path_indices.
    graph.delete_edges(_target_in=split_path_indices)

    if DEBUG_PLOT:
        debug_plot(graph, layout=layout)

    # Get incidences of all vertices which can be reached from the root. Since
    # edges pointing at split_path_indices have been deleted, none of the
    # split_path_indices will be included. Dependencies of rest_with_common will
    # only be included if they can be reached from any vertex which is itself
    # not in split_off_vertex_indices.
    rest_with_common = frozenset(graph.subcomponent(root_name, mode="out"))
    debug("rest_with_common", rest_with_common)

    # Get a set of all dependencies common to split_path_indices and the rest
    # of the graph.
    common = split_off_vertex_indices.intersection(rest_with_common)
    debug("common", common)

    # Get a set of vertices which cannot be reached from split_path_indices.
    rest_without_common = rest_with_common.difference(common)
    debug("rest_without_common", rest_without_common)

    # Get a set of split_path_indices and their dependencies which cannot be
    # reached from the rest of the graph.
    split_off_without_common = split_off_vertex_indices.difference(common)
    debug("split_off_without_common", split_off_without_common)

    if DEBUG_PLOT:
        def choose_color(index):
            if (index in split_off_without_common):
                return "green"
            elif (index in rest_without_common):
                return "red"
            else:
                return "purple"

        vertex_color = [choose_color(v.index) for v in graph.vs]

        debug_plot(
            graph,
            layout=layout,
            vertex_color=vertex_color
        )

    # Return subgraphs based on calculated sets of vertices.
    return {
        # Dependencies of split paths which can be reached from the rest of the
        # graph.
        "common": graph.induced_subgraph(common),
        # Rest of the graph (without dependencies common with split paths).
        "rest": graph.induced_subgraph(rest_without_common),
        # Split paths and their deps (unreachable from rest of the graph).
        "main": graph.induced_subgraph(split_off_without_common)
    }


def graph_is_not_empty(graph):
    return len(graph.vs) > 0


def values_for_keys(keys, d):
    return [d.get(k) for k in keys]


split_result_keys = ['common', 'rest', 'main']


def reducer(layers, split_path_spec):
    debug("reducer layers", layers)
    debug("reducer split_path_spec", split_path_spec)
    sub_splits = {}
    if isinstance(split_path_spec, dict):
        sub_splits = split_path_spec["sub_splits"]
        split_path_spec = split_path_spec["paths"]
        debug("reducer sub_splits", sub_splits)
        debug("reducer split_path_spec", split_path_spec)

    elif not isinstance(split_path_spec, list):
        raise Exception("Split path spec needs to be a list or a dict")

    # new_layers = []

    # split_off_layer = igraph.Graph(directed=True)

    # # Attempt to split all layers created so far.
    # for layer in layers:
    #     result = split(layer, split_path_spec)
    #     # If split_path_spec does not affect given layer, simply append current
    #     # layer without changes.
    #     if result is None:
    #         # debug_plot(graph)
    #         new_layers.append(layer)
    #     # If layer has been split, append last of the split layers with one that
    #     # might have been slit off in previous iteration(s), and push the rest
    #     # as they are. This way we ensure that split_paths listed in a single
    #     # array, always end up in a single layer together.
    #     else:
    #         common, rest, main = itertools.filterfalse(is_None, result)
    #         split_off_layer += main

    #         new_layers.extend(filter(
    #             graph_is_not_empty,
    #             [common, rest]
    #         ))

    # if graph_is_not_empty(split_off_layer):
    #     new_layers.append(split_off_layer)

    def split_layer_recursive(layer):
        global split_result_keys

        split_result = split(layer, split_path_spec)

        # If split_path_spec does not affect given layer, simply return current
        # layer without changes.
        if split_result is None:
            return [layer]

        def get_layer_or_recurse(key):
            debug('key', key)
            sub_split_spec = sub_splits.get(key)
            debug('sub_split_spec', sub_split_spec)
            layer = split_result.get(key)
            debug('layer', layer)
            layers = [] if layer is None else [layer]

            return (
                layers if sub_split_spec is None
                else reducer(layers, sub_split_spec)
            )

        return tlz.compose(
            tlz.remove(is_None),
            unnest_iterable,
            tlz.map(get_layer_or_recurse)
        )(split_result_keys)

    return unnest_iterable(
        map(
            split_layer_recursive,
            layers
        )
    )


def remove_added_root(graph):
    global added_root_name
    added_root = find_vertex_by_name_or_none(graph)(added_root_name)

    return graph - added_root_name if added_root else graph


def split_graph(graph, split_path_specs):
    return list(
        filter(
            graph_is_not_empty,
            map(
                remove_added_root,
                reduce(reducer, split_path_specs, [graph]),
            )
        )
    )


def debug_plot(g, **kwargs):
    if not DEBUG_PLOT:
        return

    if "label" not in g.vs:
        g.vs["label"] = [
            # remove /nix/store/HASH- prefix from labels
            re.split("^/nix/store/[a-z0-9]{32}-", name)[-1]
            for name in g.vs["name"]
        ]

    igraph.plot(
        g,
        **kwargs,
        bbox=(3840, 2160),
        margin=100,
        vertex_label_dist=-5,
        vertex_label_size=60,
        edge_color="orange",
    )


def debug_plot_with_highligth(g, vs, layout):
    vertex_color = [
        "green" if v.index in vs else "red"
        for v in g.vs
    ]
    debug_plot(
        g,
        layout=layout,
        # layout=Layout(new_coords),
        vertex_color=vertex_color
    )
