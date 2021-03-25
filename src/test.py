import unittest

import igraph as igraph
import itertools as itertools

from .main import (
  flat_map, debug, split_graph, closure_paths_to_graph,
  load_closure_graph, unnestIterable
)

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
    graph = load_closure_graph("./__test_fixtures/closure-path.json")

    base_json_plus_wrapper_script = [
      "/nix/store/d42mjlakai854fhns781453xpkhfscpj-startup-script",
      "/nix/store/21586x62x26h2nmn6n6df25yybrpnl8k-with-env-from-dir",
      "/nix/store/gg5ngl1rbb7kifwkkmq1ir9spjdpqxhr-ankisyncd-base.json"
    ]

    expected_initial_layers = [
      [
        "/nix/store/0sgd2psd7c9i2q2zyvg47dcflxv4fqjh-nss-cacert-3.60",
        "/nix/store/3wa1xwnfv8ada1za1r8m4vmsiz1jifqq-glibc-2.32-35",
        "/nix/store/48gydzv98ns14ylw7gmkx38r4gnds82m-libunistring-0.9.10",
        "/nix/store/p4ndfjdkdpmj5gd7ifk0rjdmyihnfnm8-libidn2-2.3.0",
      ],
      [
        "/nix/store/fcgyfgjhss9adn9f2jzdq5nclldi5v2l-closure",
        "/nix/store/kbz9qzjqkv2x5y4gkxcqgjfj8d0y0adh-busybox-1.32.1",
      ],
      [
        "/nix/store/21586x62x26h2nmn6n6df25yybrpnl8k-with-env-from-dir",
        "/nix/store/d42mjlakai854fhns781453xpkhfscpj-startup-script",
        "/nix/store/gg5ngl1rbb7kifwkkmq1ir9spjdpqxhr-ankisyncd-base.json",
      ],
      [
        "/nix/store/3y5s6iyzqg2rwy8qz79i5f6cfmwqiaav-attr-2.4.48",
        "/nix/store/8w2r3lp9zkqd5rgqxxx8vi9k8kf7ckw4-pcre-8.44",
        "/nix/store/camix5721pydww6zwwd4wg77krk61gf1-acl-2.2.53",
      ],
      [
        "/nix/store/wmiyjdsaydyv024al5ddqd3liljrfvk7-gnugrep-3.6",
        "/nix/store/ypsd29c5hgj1x7xz5ddffanxw5d8fh7b-coreutils-8.32",
        "/nix/store/yyy7wr7r9jwjjqkr1yn643g3wzv010zd-bash-4.4-p23",
      ],
      [
        "/nix/store/2y63mp9ln1xychnm1bhgl5r0j0islpj8-ankisyncd-2.2.0",
      ]
    ]

    all_other_paths = frozenset(graph.vs["name"]).difference(
      frozenset(unnestIterable(expected_initial_layers))
    )

    assertResult(self,
      split_graph(
        graph,
        [
          base_json_plus_wrapper_script,
          [{
            "children_of": base_json_plus_wrapper_script
          }],
          [
            "/nix/store/2y63mp9ln1xychnm1bhgl5r0j0islpj8-ankisyncd-2.2.0",
          ],
          [{
            "children_of": [
              "/nix/store/2y63mp9ln1xychnm1bhgl5r0j0islpj8-ankisyncd-2.2.0",
            ]
          }],
        ]
      ),
      expected_initial_layers + [all_other_paths]
    )


    cacert_path = "/nix/store/0sgd2psd7c9i2q2zyvg47dcflxv4fqjh-nss-cacert-3.60"

    assertResult(self,
      split_graph(
        graph,
        [
          [{
            "children_of": base_json_plus_wrapper_script
          }],
          base_json_plus_wrapper_script,
          [{
            "children_of": [
              "/nix/store/2y63mp9ln1xychnm1bhgl5r0j0islpj8-ankisyncd-2.2.0",
            ]
          }],
          [
            "/nix/store/2y63mp9ln1xychnm1bhgl5r0j0islpj8-ankisyncd-2.2.0",
          ],
        ]
      ),
      [
        # ca-cert is moved to different layre (deps of base.json)
        filter(lambda x: x != cacert_path, expected_initial_layers[0]),
        expected_initial_layers[1],
        expected_initial_layers[3],
        expected_initial_layers[4] + [cacert_path],
        expected_initial_layers[2],
        all_other_paths,
        expected_initial_layers[5]
      ]
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
    out += "],"

  return out

def directedGraph(edges):
  return igraph.Graph.TupleList(edges, directed=True)

def graphToSet(graph):
  return frozenset(graph.vs["name"])

def assertResult(self, result, expected_layers):
  try:
    expected_layers_count = len(expected_layers)
    actual_layers_count = len(result)

    self.assertEqual(
      actual_layers_count,
      expected_layers_count,
      f'Unexpected layers count, should be: {expected_layers_count}'
    )

    for index, expected_layer in enumerate(expected_layers):
      self.assertSetEqual(
        graphToSet(result[index]),
        frozenset(expected_layer),
        f'In layer index: {index}'
      )

  except AssertionError as error:
    error.args = (layers_to_error_string(result) + "\n" + error.args[0] + "\n", )
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
