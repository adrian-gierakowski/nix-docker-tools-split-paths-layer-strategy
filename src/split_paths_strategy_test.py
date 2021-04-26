import unittest

from .split_paths_strategy import split_graph

from .lib import (
    directedGraph
)

from .lib import (
    load_closure_graph,
    path_relative_to_file,
    unnest_iterable
)


if __name__ == "__main__":
    unittest.main()


class CustomAssertions:
    def assertResult(self, result, expected_layers):
        try:
            expected_layers_count = len(expected_layers)
            actual_layers_count = len(result)

            self.assertEqual(
                actual_layers_count,
                expected_layers_count,
                f"Unexpected layers count, should be: {expected_layers_count}"
            )

            for index, expected_layer in enumerate(expected_layers):
                self.assertSetEqual(
                    vertexNames(result[index]),
                    frozenset(expected_layer),
                    f"In layer index: {index}"
                )

        except AssertionError as error:
            error.args = (
                layers_to_error_string(result) + "\n" + error.args[0] + "\n",
            )
            raise

    def splitGraphAndAssert(self, edges, split_path_specs, expected_layers):
        self.assertResult(
            split_graph(
                directedGraph(edges),
                split_path_specs
            ),
            expected_layers
        )


class TestSplitGraph(unittest.TestCase, CustomAssertions):

    # def test_split_below():

    def test_degenerate(self):
        self.splitGraphAndAssert(
            edges=[],
            split_path_specs=[],
            expected_layers=[]
        )

        self.splitGraphAndAssert(
            edges=[],
            split_path_specs=[
                ["app"]
            ],
            expected_layers=[]
        )

        edges = [("app", "app-dep")]

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[],
            expected_layers=[
                ["app", "app-dep"]
            ]
        )

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                ["app"]
            ],
            expected_layers=[
                ["app", "app-dep"]
            ]
        )

    def test_simple(self):
        edges = [
            ("app", "app-dep"),
            ("bash", "libc")
        ]

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                ["app"]
            ],
            expected_layers=[
                ["bash", "libc"],
                ["app", "app-dep"]
            ]
        )

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                ["bash"]
            ],
            expected_layers=[
                ["app", "app-dep"],
                ["bash", "libc"]
            ]
        )

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                ["app-dep"]
            ],
            expected_layers=[
                ["app", "bash", "libc"],
                ["app-dep"]
            ]
        )

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                ["libc"]
            ],
            expected_layers=[
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

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                ["app"]
            ],
            expected_layers=[
                ["libc"],
                ["bash"],
                ["app", "app-dep"]
            ]
        )

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                ["bash"]
            ],
            expected_layers=[
                ["libc"],
                ["app", "app-dep"],
                ["bash"]
            ]
        )

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                ["app-dep"]
            ],
            expected_layers=[
                ["libc"],
                ["app", "bash"],
                ["app-dep"]
            ]
        )

    def test_2_splits(self):
        edges = [
            ("app", "app-dep"),
            ("app-dep", "libc"),
            ("script", "script-dep"),
            ("bash", "libc")
        ]

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                ["app"]
            ],
            expected_layers=[
                ["libc"],
                ["script", "script-dep", "bash"],
                ["app", "app-dep"]
            ]
        )

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                ["app"],
                ["script"]
            ],
            expected_layers=[
                ["libc"],
                ["bash"],
                ["script", "script-dep"],
                ["app", "app-dep"]
            ]
        )

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                ["script"],
                ["app"]
            ],
            expected_layers=[
                ["libc"],
                ["bash"],
                ["app", "app-dep"],
                ["script", "script-dep"]
            ]
        )

    def test_children_of(self):
        edges = [
            ("app", "app-dep"),
            ("app-dep", "app-transitive-dep"),
            ("app", "common-dep-1"),
            ("app-dep", "common-dep-2"),
            ("bash", "common-dep-2"),
            ("script", "common-dep-1")
        ]

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                [{"children_of": "app"}]
            ],
            expected_layers=[
                ["common-dep-2"],
                ["app", "bash", "script"],
                ["app-dep", "app-transitive-dep", "common-dep-1"]
            ]
        )

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                [{"children_of": "app"}],
                ["app"],
            ],
            expected_layers=[
                ["common-dep-2"],
                ["bash", "script"],
                ["app"],
                ["app-dep", "app-transitive-dep", "common-dep-1"]
            ]
        )

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                ["app"],
                [{"children_of": "app"}]
            ],
            expected_layers=[
                # NOTE: common-dep-2 ended up in the "common" layer since it's
                # a dep of script as well as the app. Since we split on "app"
                # first, it landed in the common layer, and so during the second
                # split, it was not a "child" of app any more.
                ["common-dep-2", "common-dep-1"],
                ["bash", "script"],
                ["app"],
                ["app-dep", "app-transitive-dep"],
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

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                all_scripts
            ],
            expected_layers=[
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

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                all_scripts,
                [{"children_of": all_scripts}]
            ],
            # NOTE: this grouping seems to be more favourable, however the order
            # of te layer is not, assuming that the last layer is treated as
            # most significant (least likely to get combined with a neighbour in
            # case number of produced layers is > maxLayers)
            expected_layers=[
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

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                [{"children_of": all_scripts}]
            ],
            expected_layers=[
                [
                    "script-1",
                    "script-3",
                    "top-level"
                ],
                [
                    "script-2",
                    "coreutils",
                    "gnugrep",
                    "curl",
                    "bash",
                    "libc"
                ]
            ]
        )

        self.splitGraphAndAssert(
            edges,
            split_path_specs=[
                [{"children_of": all_scripts}],
                all_scripts
            ],
            expected_layers=[
                [
                    "top-level",
                ],
                [
                    "script-1",
                    "script-3",
                ],
                [
                    "coreutils",
                    "gnugrep",
                    "curl",
                    "bash",
                    "libc",
                ],
                [
                    "script-2",
                ]
            ]
        )

    # WIP
    def test_real(self):
        graph = load_closure_graph(path_relative_to_file(
            __file__,
            "__test_fixtures/real-references-graph.json"
        ))

        base_json_plus_wrapper_script = [
            "/nix/store/d42mjlakai854fhns781453xpkhfscpj-startup-script",
            "/nix/store/21586x62x26h2nmn6n6df25yybrpnl8k-with-env-from-dir",
            "/nix/store/gg5ngl1rbb7kifwkkmq1ir9spjdpqxhr-ankisyncd-base.json"
        ]

        expected_initial_layers = [
            [
                "/nix/store/0sgd2psd7c9i2q2zyvg47dcflxv4fqjh-nss-cacert-3.60",
                "/nix/store/p4ndfjdkdpmj5gd7ifk0rjdmyihnfnm8-libidn2-2.3.0",
                "/nix/store/48gydzv98ns14ylw7gmkx38r4gnds82m-libunistring-0.9.10",
                "/nix/store/3wa1xwnfv8ada1za1r8m4vmsiz1jifqq-glibc-2.32-35"
            ],
            [
                "/nix/store/fcgyfgjhss9adn9f2jzdq5nclldi5v2l-closure",
                "/nix/store/kbz9qzjqkv2x5y4gkxcqgjfj8d0y0adh-busybox-1.32.1"
            ],
            [
                "/nix/store/gg5ngl1rbb7kifwkkmq1ir9spjdpqxhr-ankisyncd-base.json",
                "/nix/store/d42mjlakai854fhns781453xpkhfscpj-startup-script",
                "/nix/store/21586x62x26h2nmn6n6df25yybrpnl8k-with-env-from-dir"
            ],
            [
                "/nix/store/3y5s6iyzqg2rwy8qz79i5f6cfmwqiaav-attr-2.4.48",
                "/nix/store/camix5721pydww6zwwd4wg77krk61gf1-acl-2.2.53",
                "/nix/store/8w2r3lp9zkqd5rgqxxx8vi9k8kf7ckw4-pcre-8.44"
            ],
            [
                "/nix/store/wmiyjdsaydyv024al5ddqd3liljrfvk7-gnugrep-3.6",
                "/nix/store/yyy7wr7r9jwjjqkr1yn643g3wzv010zd-bash-4.4-p23",
                "/nix/store/ypsd29c5hgj1x7xz5ddffanxw5d8fh7b-coreutils-8.32"
            ],
            [
                "/nix/store/2y63mp9ln1xychnm1bhgl5r0j0islpj8-ankisyncd-2.2.0"
            ]
        ]

        all_other_paths = frozenset(graph.vs["name"]).difference(
            frozenset(unnest_iterable(expected_initial_layers))
        )

        self.assertResult(
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

        last_layer = [
            "/nix/store/d42mjlakai854fhns781453xpkhfscpj-startup-script",
            "/nix/store/21586x62x26h2nmn6n6df25yybrpnl8k-with-env-from-dir"
        ]

        self.assertResult(
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
                frozenset(expected_initial_layers[0]).difference(
                    frozenset([cacert_path])
                ),
                expected_initial_layers[1],
                frozenset(expected_initial_layers[2]).difference(
                    frozenset(last_layer)
                ),
                expected_initial_layers[3],
                expected_initial_layers[4] + [cacert_path],
                expected_initial_layers[5],
                all_other_paths,
                last_layer
            ]
        )

#
# Helpers
#


def layers_to_error_string(layers):
    out = "\n::::LAYERS:::::"
    for index, layer in enumerate(layers):
        out += f"\nlayer index: {index}\n[\n"
        for v in layer.vs["name"]:
            out += f"    \"{v}\",\n"
        out += "],"

    return out


def vertexNames(graph):
    return frozenset(graph.vs["name"])
