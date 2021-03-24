import unittest

import igraph as igraph
import itertools as itertools

from .main import flat_map, debug, print_vs, split_graph, closure_paths_to_graph, load_json

class TestSplitGraph(unittest.TestCase):

  def test_degenerate(self):
    testSplitGraph(self,
      edges = [],
      split_path_specs = [],
      expected_layers = []
    )

    testSplitGraph(self,
      edges = [],
      split_path_specs = [
        ["app"]
      ],
      expected_layers = []
    )

    edges = [("app", "app-dep")]

    testSplitGraph(self,
      edges,
      split_path_specs = [],
      expected_layers = [
        ["app", "app-dep"]
      ]
    )

    testSplitGraph(self,
      edges,
      split_path_specs = [
        ["app"]
      ],
      expected_layers = [
        ["app", "app-dep"]
      ]
    )

  def test_simple(self):
    edges = [
      ("app", "app-dep"),
      ("bash", "libc")
    ]

    testSplitGraph(self,
      edges,
      split_path_specs = [
        ["app"]
      ],
      expected_layers = [
        ["bash", "libc"],
        ["app", "app-dep"]
      ]
    )

    testSplitGraph(self,
      edges,
      split_path_specs = [
        ["bash"]
      ],
      expected_layers = [
        ["app", "app-dep"],
        ["bash", "libc"]
      ]
    )

    testSplitGraph(self,
      edges,
      split_path_specs = [
        ["app-dep"]
      ],
      expected_layers = [
        ["app", "bash", "libc"],
        ["app-dep"]
      ]
    )

    testSplitGraph(self,
      edges,
      split_path_specs = [
        ["libc"]
      ],
      expected_layers = [
        ["app", "bash", "app-dep"],
        ["libc"]
      ]
    )


  def test_simple_with_common(self):
    edges = [
      ("app", "app-dep"),
      ("app-dep", "libc"),
      ("bash", "libc")
    ]

    testSplitGraph(self,
      edges,
      split_path_specs = [
        ["app"]
      ],
      expected_layers = [
        ["libc"],
        ["bash"],
        ["app", "app-dep"]
      ]
    )

    testSplitGraph(self,
      edges,
      split_path_specs = [
        ["bash"]
      ],
      expected_layers = [
        ["libc"],
        ["app", "app-dep"],
        ["bash"]
      ]
    )

    testSplitGraph(self,
      edges,
      split_path_specs = [
        ["app-dep"]
      ],
      expected_layers = [
        ["libc"],
        ["app", "bash"],
        ["app-dep"]
      ]
    )


  def test_2_splits(self):
    edges = [
      ("app", "app-dep"),
      ("app-dep", "libc"),
      ("script-1", "script-1-dep"),
      ("bash", "libc")
    ]

    testSplitGraph(self,
      edges,
      split_path_specs = [
        ["app"]
      ],
      expected_layers = [
        ["libc"],
        ["script-1", "script-1-dep", "bash"],
        ["app", "app-dep"]
      ]
    )

    testSplitGraph(self,
      edges,
      split_path_specs = [
        ["script-1"],
        ["app"]
      ],
      expected_layers = [
        ["libc"],
        ["bash"],
        ["script-1", "script-1-dep"],
        ["app", "app-dep"]
      ]
    )

    # Order of split_path_specs determines the order of produced layers.
    testSplitGraph(self,
      edges,
      split_path_specs = [
        ["app"],
        ["script-1"]
      ],
      expected_layers = [
        ["libc"],
        ["bash"],
        ["app", "app-dep"],
        ["script-1", "script-1-dep"]
      ]
    )

  def test_children_of(self):
    edges = [
      ("app", "app-dep-1"),
      ("app", "app-dep-2"),
      ("app-dep-1", "libc"),
      ("bash", "libc"),
      ("script-1", "app-dep-2")
    ]

    testSplitGraph(self,
      edges,
      split_path_specs = [
        [{ "children_of": "app" }],
        ["app"],
      ],
      expected_layers = [
        ["libc"],
        ["bash", "script-1"],
        ["app-dep-1", "app-dep-2"],
        ["app"]
      ]
    )

    testSplitGraph(self,
      edges,
      split_path_specs = [
        ["app"],
        [{ "children_of": "app" }]
      ],
      expected_layers = [
        # NOTE: app-dep-2 ended up in the "common" layer since it's also a dep
        # of script-1. Since we split on "add" first, it landed in the common
        # layer, and so during the second split, it was not a "child" of
        # app any more.
        ["libc", "app-dep-2"],
        ["bash", "script-1"],
        ["app"],
        ["app-dep-1"],
      ]
    )


  def test_children_of_many(self):
    edges = [
      ("script-1", "script-2"),
      ("script-1", "coreutils"),
      ("script-2", "gnugrep"),
      ("script-3", "curl"),
      ("script-1", "bash"),
      ("script-2", "bash"),
      ("script-3", "bash"),
      ("bash", "libc"),
      ("curl", "libc"),
      # as if added in "contents"
      ("top-level", "script-1"),
      ("top-level", "script-3"),
      ("top-level", "bash")
    ]

    all_scripts = ["script-1", "script-2", "script-3"]

    testSplitGraph(self,
      edges,
      split_path_specs = [
        all_scripts
      ],
      expected_layers = [
        ["bash", "libc"],
        ["top-level"],
        [
          "script-1",
          "script-2",
          "coreutils",
          "gnugrep",
          "script-3",
          "curl"
        ]
      ]
    )

    testSplitGraph(self,
      edges,
      split_path_specs = [
        [{ "children_of": all_scripts }],
        all_scripts
      ],
      expected_layers = [
        ["top-level"],
        [
          "bash",
          "libc",
          "coreutils",
          "gnugrep",
          "curl"
        ],
        [
          "script-1",
          "script-2",
          "script-3"
        ]
      ]
    )

    testSplitGraph(self,
      edges,
      split_path_specs = [
        all_scripts,
        [{ "children_of": all_scripts }]
      ],
      # NOTE: this grouping seems to be more favourable, however the order
      # of te layer is not, assuming that the last layer is treated as most
      # significant (least likely to get combined with a neighbour in case
      # number of produced layers is > maxLayers)
      expected_layers = [
        ["bash", "libc"],
        ["top-level"],
        [
          "script-1",
          "script-2",
          "script-3"
        ],
        [
          "coreutils",
          "gnugrep",
          "curl"
        ]
      ]
    )

  # WIP
  def test_real(self):
    graph = closure_paths_to_graph(load_json("./__test_fixtures/closure-path.json"))
    assertResult(self,
      split_graph(
        graph,
        [["/nix/store/zr5y2gv34lyflyfi33hlk28ppk31apr6-gfortran-9.3.0-lib"]]
      ),
      []
    )

class TestClosurePathToGraph(unittest.TestCase):

  def one(self):
    closure_paths = [
      {
        "closureSize": 1,
        "narHash": "sha256:a",
        "narSize": 2,
        "path": "A",
        "references": [
          # most of the time references contain self path (but not always, not
          # sure why)
          "A",
          "B",
          "C"
        ]
      },
      {
        "closureSize": 3,
        "narHash": "sha256:b",
        "narSize": 4,
        "path": "B",
        "references": [
          "C"
        ]
      },
      {
        "closureSize": 5,
        "narHash": "sha256:c",
        "narSize": 6,
        "path": "C",
        "references": [
          "C"
        ]
      }
    ]

    graph = closure_paths_to_graph(closure_paths)

    self.assertEqual(3, len(graph.vs))

    def vertexPropsAsArray(v):
      return [v["name"], v["closureSize"], v["narSize"]]

    self.assertListEqual(
      vertexPropsAsArray(graph.vs[0]),
      ["A", 1, 2]
    )

    self.assertListEqual(
      vertexPropsAsArray(graph.vs[1]),
      ["B", 3, 4]
    )

    self.assertListEqual(
      vertexPropsAsArray(graph.vs[2]),
      ["C", 5, 6]
    )

    self.assertEqual(3, len(graph.es))

    def edgePropsAsArray(e):
      return [e["source"], e["target"]]

    self.assertListEqual(
      edgePropsAsArray(graph.es[0]),
      ["A", "B"]
    )

    self.assertListEqual(
      edgePropsAsArray(graph.es[1]),
      ["A", "C"]
    )

    self.assertListEqual(
      edgePropsAsArray(graph.es[2]),
      ["B", "C"]
    )


#
# Helpers
#

def layers_to_error_string(layers):
  out = "\n::::LAYERS:::::"
  for index, layer in enumerate(layers):
    out += f"\nlayer index: {index}\n[\n"
    for v in layer.vs["name"]:
      out += f"  \"{v}\",\n"
    out += "]"

  return out

def directedGraph(edges):
  return igraph.Graph.TupleList(edges, directed=True)

def graphToSet(graph):
  return frozenset(graph.vs["name"])

def assertResult(self, result, expected_layers):
  try:
    for index, expected_layer in enumerate(expected_layers):
      if index >= len(result):
        print_layers(result)
        self.assertTrue(
          False,
          f'Layer with index: {index} does not exist'
        )
      else:
        self.assertSetEqual(
          graphToSet(result[index]),
          set(expected_layer),
          f'In layer index: {index}'
        )

  except AssertionError as error:
    error.args = (error.args[0] + "\n" + layers_to_error_string(result), )
    raise

def testSplitGraph(self, edges, split_path_specs, expected_layers):
  assertResult(self,
    split_graph(
      directedGraph(edges),
      split_path_specs
    ),
    expected_layers
  )

if __name__ == '__main__':
  unittest.main()
