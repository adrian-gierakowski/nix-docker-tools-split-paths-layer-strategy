from toolz import curried as tlz
from toolz import curry

from . import lib as lib
from . import subcomponent as subcomponent
from . import split_paths as split_paths

from .lib import (
    # references_graph_to_igraph
    debug,
    pick_attrs
)

# from . import lib as lib

funcs = tlz.merge(
    pick_attrs(
        [
            "flatten",
            "over",
            "split_every",
            "limit_layers"
        ],
        lib
    ),
    pick_attrs(
        [
            "subcomponent_in",
            "subcomponent_out",
        ],
        subcomponent
    ),
    pick_attrs(
        [
            "split_paths",
        ],
        split_paths
    )
)

debug('funcs', funcs)


@curry
def nth_or_none(index, xs):
    try:
        return xs[index]
    except IndexError:
        return None


def preapply_func(func_call_data):
    [func_name, *args] = func_call_data
    debug("func_name", func_name)
    debug("args", args)
    debug('func_name in ["over"]', func_name in ["over"])
    if func_name in ["over"]:
        [first_arg, second_arg] = args
        args = [first_arg, preapply_func(second_arg)]

    return funcs[func_name](*args)


@curry
def pipeline(pipeline, data):
    debug("pipeline", pipeline)
    partial_funcs = list(tlz.map(preapply_func, pipeline))
    debug('partial_funcs', partial_funcs)
    return tlz.pipe(
        data,
        *partial_funcs
    )


funcs["pipeline"] = pipeline
