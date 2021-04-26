import unittest
from .process_pipeline import pipeline

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
        ("E", "F"),
        ("B", "G"),
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


if __name__ == "__main__":
    unittest.main()


class Test(unittest.TestCase, CustomAssertions):

    def test_1(self):
        stages = [
            ["split_paths", ["B"]],
            [
                "over",
                "main",
                [
                    "pipeline",
                    [
                        ["subcomponent_in", ["B"]],
                        [
                            "over",
                            "rest",
                            ["split_every", 1]
                        ]
                    ]
                ]
            ],
            ["flatten"],
            ["limit_layers", 5]
        ]

        result = list(pipeline(stages, makeTestGraph()))

        print(list(map(lambda g: g.vs["name"], result)))

        # "B"" separated from the rest by split_paths and subcomponent_in
        self.assertGraphsEqual(
            directedGraph([], ["B"]),
            result[0]
        )

        # Deps of "B", split into individual layers by "split_every"
        self.assertGraphsEqual(
            directedGraph([], ["D"]),
            result[1]
        )

        self.assertGraphsEqual(
            directedGraph([], ["E"]),
            result[2]
        )

        self.assertGraphsEqual(
            directedGraph([], ["F"]),
            result[3]
        )

        # "rest" output of "split_paths" with # "G" merged into it by
        # "limit_layers"
        self.assertGraphsEqual(
            directedGraph(
                [
                    ("Root1", "A"),
                    ("A", "C"),
                    ("Root3", "C"),
                ],
                ["Root2", "G"]
            ),
            result[4]
        )



