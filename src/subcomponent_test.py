import unittest

from .subcomponent import (
    subcomponent_out,
    subcomponent_in
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
        ("A", "C"),
        ("B", "D"),
        ("B", "E"),
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

    def assertResultKeys(self, result):
        self.assertListEqual(
            list(result.keys()),
            ["main", "rest"]
        )

        return result


class TestSubcomponent(unittest.TestCase, CustomAssertions):

    def test_empty_paths(self):
        def test(func):
            input_graph = makeTestGraph()

            result = self.assertResultKeys(
                func(input_graph, [])
            )

            self.assertGraphsEqual(
                result["main"],
                emptyDirectedGraph()
            )

            self.assertGraphsEqual(
                result["rest"],
                input_graph
            )

        test(subcomponent_out)
        test(subcomponent_in)

    def test_empty_graph(self):
        def test(func):
            empty_graph = emptyDirectedGraph()

            def test_empty(paths):
                result = self.assertResultKeys(
                    func(empty_graph, paths)
                )

                self.assertGraphsEqual(
                    result["main"],
                    empty_graph
                )

                self.assertGraphsEqual(
                    result["rest"],
                    empty_graph
                )

            test_empty([])
            test_empty(["B"])

        test(subcomponent_out)
        test(subcomponent_in)

    def test_subcomponent_out(self):
        result = self.assertResultKeys(
            subcomponent_out(makeTestGraph(), ["B"])
        )

        self.assertGraphsEqual(
            result["main"],
            directedGraph(
                [
                    ("B", "D"),
                    ("B", "E")
                ]
            )
        )

        self.assertGraphsEqual(
            result["rest"],
            directedGraph(
                [
                    ("Root1", "A"),
                    ("A", "C"),
                    ("Root3", "C")
                ],
                ["Root2"]
            )
        )

    def test_subcomponent_out_multi(self):
        result = self.assertResultKeys(
            subcomponent_out(makeTestGraph(), ["B", "Root3"])
        )

        self.assertGraphsEqual(
            result["main"],
            directedGraph(
                [
                    ("B", "D"),
                    ("B", "E"),
                    ("Root3", "C")
                ]
            )
        )

        self.assertGraphsEqual(
            result["rest"],
            directedGraph([("Root1", "A")], ["Root2"])
        )

    def test_subcomponent_in(self):
        result = self.assertResultKeys(
            subcomponent_in(makeTestGraph(), ["B"])
        )

        self.assertGraphsEqual(
            result["main"],
            directedGraph(
                [
                    ("Root1", "A"),
                    ("A", "B"),
                    ("Root2", "B")
                ]
            )
        )

        self.assertGraphsEqual(
            result["rest"],
            directedGraph([("Root3", "C")], ["D", "E"])
        )

    def test_subcomponent_in_multi(self):
        result = self.assertResultKeys(
            subcomponent_in(makeTestGraph(), ["B", "Root3"])
        )

        self.assertGraphsEqual(
            result["main"],
            directedGraph(
                [
                    ("Root1", "A"),
                    ("A", "B"),
                    ("Root2", "B"),
                ],
                ["Root3"]
            )
        )

        self.assertGraphsEqual(
            result["rest"],
            directedGraph([], ["C", "D", "E"])
        )
