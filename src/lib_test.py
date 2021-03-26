import unittest

from .lib import references_graph_to_igraph

if __name__ == "__main__":
    unittest.main()


class TestLib(unittest.TestCase):

    def test_references_graph_to_igraph(self):
        references_graph = [
            {
                "closureSize": 1,
                "narHash": "sha256:a",
                "narSize": 2,
                "path": "A",
                "references": [
                    # most of the time references contain self path (but not
                    # always, not sure why)
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

        graph = references_graph_to_igraph(references_graph)

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
