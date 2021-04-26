from toolz import curry
from toolz import curried as tlz
from operator import attrgetter

from .lib import (
    debug,
    find_vertex_by_name_or_none,
    is_None,
    subcomponent_multi
)


@curry
def subcomponent(mode, paths, graph):
    path_indices = tlz.compose(
        tlz.map(attrgetter('index')),
        tlz.remove(is_None),
        tlz.map(find_vertex_by_name_or_none(graph))
    )(paths)

    debug("path_indices", path_indices)

    main_indices = list(subcomponent_multi(graph, path_indices, mode))

    debug('main_indices', main_indices)

    return {
        "main": graph.induced_subgraph(main_indices),
        "rest": graph - main_indices
    }


subcomponent_in = subcomponent("in")

subcomponent_out = subcomponent("out")
