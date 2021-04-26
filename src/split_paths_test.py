import unittest
from toolz import curry

from .split_paths import (
    split_paths
)

from .lib import (
    directedGraph,
    emptyDirectedGraph
)


if __name__ == "__main__":
    unittest.main()


def makeTestGraph():
    edges = [
        ("Root1", "A"),
        ("A", "B"),
        ("A", "D"),
        ("D", "E"),
        ("B", "D"),
        ("B", "F"),
        ("Root2", "B"),
        ("Root3", "C"),
    ]

    return directedGraph(edges)


def graphVertexIndexToName(graph, index):
    return graph.vs[index]["name"]


def edgesAsSet(graph):
    return frozenset(
        (
            graphVertexIndexToName(graph, e.source),
            graphVertexIndexToName(graph, e.target)
        ) for e in graph.es
    )


class CustomAssertions:
    def assertGraphsEqual(self, g1, g2):
        self.assertSetEqual(
            frozenset(g1.vs["name"]),
            frozenset(g2.vs["name"])
        )

        self.assertSetEqual(
            edgesAsSet(g1),
            edgesAsSet(g2)
        )

    @curry
    def assertResultKeys(self, keys, result):
        self.assertListEqual(
            list(result.keys()),
            keys
        )

        return result


class TestSplitPaths(unittest.TestCase, CustomAssertions):

    def test_empty_paths(self):
        def test(func):
            input_graph = makeTestGraph()

            result = self.assertResultKeys(
                ["rest"],
                func(input_graph, [])
            )

            self.assertGraphsEqual(
                result["rest"],
                input_graph
            )

        test(split_paths)

    def test_empty_graph(self):
        def test(func):
            empty_graph = directedGraph([])

            def test_empty(paths):
                result = self.assertResultKeys(
                    ["rest"],
                    func(empty_graph, paths)
                )

                self.assertGraphsEqual(
                    result["rest"],
                    empty_graph
                )

            test_empty([])
            test_empty(["B"])

        test(split_paths)

    def test_split_paths_single(self):
        result = self.assertResultKeys(
            ["common", "rest", "main"],
            split_paths(makeTestGraph(), ["B"])
        )

        self.assertGraphsEqual(
            result["main"],
            directedGraph(
                [
                    ("B", "F")
                ]
            )
        )

        self.assertGraphsEqual(
            result["rest"],
            directedGraph(
                [
                    ("Root1", "A"),
                    ("Root3", "C")
                ],
                ["Root2"]
            )
        )

        self.assertGraphsEqual(
            result["common"],
            directedGraph([("D", "E")])
        )

    def test_split_paths_multi(self):
        result = self.assertResultKeys(
            ["common", "rest", "main"],
            split_paths(makeTestGraph(), ["B", "Root3"])
        )

        self.assertGraphsEqual(
            result["main"],
            directedGraph(
                [
                    ("B", "F"),
                    ("Root3", "C")
                ]
            )
        )

        self.assertGraphsEqual(
            result["rest"],
            directedGraph([("Root1", "A")], ["Root2"])
        )

        self.assertGraphsEqual(
            result["common"],
            directedGraph([("D", "E")])
        )

    def test_split_no_common(self):
        result = self.assertResultKeys(
            ["rest", "main"],
            split_paths(makeTestGraph(), ["D"])
        )

        self.assertGraphsEqual(
            result["main"],
            directedGraph([("D", "E")])
        )

        self.assertGraphsEqual(
            result["rest"],
            directedGraph([
                ("Root1", "A"),
                ("A", "B"),
                ("B", "F"),
                ("Root2", "B"),
                ("Root3", "C"),
            ])
        )

