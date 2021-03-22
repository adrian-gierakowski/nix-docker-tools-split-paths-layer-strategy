from igraph import *
from itertools import chain
from functools import reduce
from functools import partial
from operator import is_not

g_maybe_no_root = Graph.TupleList(
  [
    ("app", "app-config"),
    ("app", "script3"),
    ("app", "app-dep1"),
    ("app", "app-dep2"),
    ("app-dep2", "app-dep2_dep1"),
    ("app-dep2", "libc"),
    ("script1", "script1-dep1"),
    ("script1", "script2"),
    ("script1", "bash"),
    ("script1", "coreutils"),
    ("script2", "bash"),
    ("script3", "bash"),
    ("bash", "libc"),
    ("curl", "libc"),
    ("coreutils", "libc"),
    ("top-level", "curl"),
    ("top-level", "coreutils"),
    ("top-level", "bash")

  ],
  directed=True
)

# g_maybe_no_root.vs.find("bla")
# quit()

def print_vs(g):
  for v in g.vs: print(v)

# print_vs(g_maybe_no_root)
# print(g_maybe_no_root.subcomponent("bash", mode="out"))
# print_vs(g_maybe_no_root.induced_subgraph(g_maybe_no_root.subcomponent("bash", mode="out")))

def my_plot(g):
  g.vs["label"] = g.vs["name"]
  g.vs["label_size"] = 24
  plot(g, layout=g.layout("tree"))

def plot_induced(g, vs):
  my_plot(g.induced_subgraph(vs))

def add_root(g, added_root_name = "__root__"):
  # my_plot(g)
  roots = g.vs.select(lambda v: len(g.predecessors(v)) == 0)
  root_names = roots["name"]
  if len(root_names) == 1:
    return g, root_names[0]
  else:
    edges = [(added_root_name, v) for v in root_names]
    g_with_root = g + added_root_name + edges
    # my_plot(g_with_root)
    return g_with_root, added_root_name



def flat_map(f, xs):
  ys = []
  for x in xs:
    ys.extend(f(x))
  return ys

def subcomponent_multi(g, vs):
  return flat_map(
    lambda v : g.subcomponent(v, mode="out"),
    vs
  )

split_paths_arrays = [["app"], [{ "children_of": "app" }], ["script1", "script3"]]
# split_paths_arrays = [["app"], ["script1", "script3"]]


def flatten(data):
  result = []
  for item in data:
    if isinstance(item, list):
      result.extend(flatten(item))
    else:
      result.append(item)
  return result

def find_vertex_by_name_or_none(graph, name):
  try:
    return graph.vs.find(name)
  # This will be thrown if any of the paths is not found in g_in
  except ValueError:
    return None


def map_split_path_spec_to_indices(graph):
  def map_split_path_spec_to_indices_inner(split_path_spec):
    print('split_path_spec', split_path_spec)
    if isinstance(split_path_spec, dict):
      if 'children_of' in split_path_spec:
        parent_v = find_vertex_by_name_or_none(graph, split_path_spec['children_of'])
        if parent_v == None:
          return []
        else:
          return graph.successors(parent_v)
      else:
        raise Exception("Unexpected split path spec: dics with invalid keys")

    else:
      vertex = find_vertex_by_name_or_none(graph, split_path_spec)
      if vertex == None:
        return []
      else:
        return [vertex.index]

  return map_split_path_spec_to_indices_inner

def unnestIterable(xs):
  return list(chain.from_iterable(xs))

def split(split_path_specs):
  def split_innner(g_in):
    print('____')
    print('split_path_specs:', split_path_specs)
    print('g_in:', g_in)

    split_path_indices = unnestIterable(map(
      map_split_path_spec_to_indices(g_in),
      split_path_specs
    ))

    print("split_path_indices:", split_path_indices)

    if len(split_path_indices) == 0:
      return None

    g, root_name = add_root(g_in)

    g = g if g is not g_in else g.copy()

    # find with name is constant time

    # quit()

    # my_plot(g)
    print('root_name', root_name)
    split_off_vertex_indices = set(subcomponent_multi(g, split_path_indices))

    print('split_off_vertex_indices', split_off_vertex_indices)
    g.delete_edges(_target_in = split_path_indices)

    # my_plot(g)

    rest_with_common = set(g.subcomponent(root_name, mode="out"))

    print('rest_with_common', rest_with_common)
    common = split_off_vertex_indices.intersection(rest_with_common)
    print('common', common)
    rest_without_common = rest_with_common.difference(common)
    print('rest_without_common', rest_without_common)
    split_off_without_common = split_off_vertex_indices.difference(common)
    print('split_off_without_common', split_off_without_common)

    return [
      g.induced_subgraph(split_off_without_common),
      g.induced_subgraph(rest_without_common),
      g.induced_subgraph(common)
    ]

  return split_innner

def reducer(acc, edge_cut_spec):
  print('reducer edge_cut_spec', edge_cut_spec)
  print('acc', acc)
  graphs = []
  split_off_graph = Graph(directed=True)
  for graph in acc:
    result = split(edge_cut_spec)(graph)
    if result == None:
      graphs.append(graph)
    else:
      head, *tail = result
      split_off_graph += head
      graphs.extend(tail)

  graphs.append(split_off_graph)
  return graphs

# print(list(chain.from_iterable([[1,2],[2,3]])))
# quit()
layers_as_graphs = reduce(reducer, split_paths_arrays, [g_maybe_no_root])

print('layers_as_graphs', layers_as_graphs)
for layer in layers_as_graphs:
  print(layer)
  print_vs(layer)

  # plot_induced(g, split_off_vertex_indices)
  # plot_induced(g, rest_with_common)
  # plot_induced(g, common)
  # plot_induced(g, rest_without_common)
  # plot_induced(g, split_off_without_common)

# split_off_g = g.induced_subgraph(split_off_vertex_indices)

# print(split_off_vertex_indices)
# my_plot(g)

# my_plot(rest)
# my_plot(split_off_g )

# my_plot(g - split_paths)

# g_without_split_patsh = (g - split_paths)
# my_plot(g_without_split_patsh - g_without_split_patsh.vs.select(_degree=0))
