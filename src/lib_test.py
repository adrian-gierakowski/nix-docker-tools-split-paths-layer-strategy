import unittest

from .lib import references_graph_to_igraph, print_vs, find_vertex_by_name_or_none

if __name__ == "__main__":
    unittest.main()


class TestLib(unittest.TestCase):

    def test_references_graph_to_igraph(self):
        references_graph = [
            {
                "closureSize": 3,
                "narHash": "sha256:b",
                "narSize": 0,
                "path": "D",
                "references": [
                ]
            },
            {
                "closureSize": 3,
                "narHash": "sha256:b",
                "narSize": 4,
                "path": "B",
                "references": [
                ]
            },
            {
                "closureSize": 3,
                "narHash": "sha256:b",
                "narSize": 5,
                "path": "E",
                "references": [
                ]
            },
            {
                "closureSize": 1,
                "narHash": "sha256:a",
                "narSize": 10,
                "path": "A",
                "references": [
                    # most of the time references contain self path (but not
                    # always, not sure why)
                    "C",
                    "B",
                ]
            },
            {
                "closureSize": 5,
                "narHash": "sha256:c",
                "narSize": 6,
                "path": "C",
                "references": [
                    "E",
                    "D"
                ]
            }
        ]

        graph = references_graph_to_igraph(references_graph)

        print(graph)
        print_vs(graph)
        print(graph.dfs(find_vertex_by_name_or_none(graph)("A").index))
        print([
            (graph.vs[x]["name"], graph.vs[x]["narSize"]) for x in
            graph.dfs(find_vertex_by_name_or_none(graph)("A").index)[0]
        ])
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
