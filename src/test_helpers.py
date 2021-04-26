import igraph as igraph


def directedGraph(edges, vertices=None):
    graph = igraph.Graph.TupleList(edges, directed=True)
    return graph if vertices is None else graph + vertices
