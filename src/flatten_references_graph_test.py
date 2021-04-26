import unittest
import inspect as inspect
from .flatten_references_graph import flatten_references_graph
from .lib import path_relative_to_file, load_json

if __name__ == "__main__":
    unittest.main()


class Test(unittest.TestCase):

    def test_flatten_references_graph(self):
        references_graph = load_json(path_relative_to_file(
            __file__,
            "__test_fixtures/fake-references-graph.json"
        ))

        strategy = {
            "algo": "split_by_paths",
            "args": [
                [
                    ["B"]
                ]
            ]
        }

        result = flatten_references_graph(references_graph, strategy)

        self.assertEqual(
            result,
            [['C'], ['A'], ['B']]
        )

        strategy = {
            "algo": "split_by_paths",
            "paths": ["C"],
            "sub_split": {
                "main": {
                    "algo": "split_by_paths",
                    "paths": [["B"]]
                }
            }
        }

        result = flatten_references_graph(references_graph, strategy)

        self.assertEqual(
            result,
            [['C'], ['A'], ['B']]
        )
