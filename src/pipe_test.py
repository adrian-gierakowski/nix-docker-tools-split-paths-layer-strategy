import unittest
from .pipe import pipe

from . import test_helpers as th

from .lib import (
    directed_graph,
)


if __name__ == "__main__":
    unittest.main()


def make_test_graph():
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

    return directed_graph(edges)


if __name__ == "__main__":
    unittest.main()


class Test(
    unittest.TestCase,
    th.CustomAssertions
):

    def test_1(self):
        pipeline = [
            ["split_paths", ["B"]],
            [
                "over",
                "main",
                [
                    "pipe",
                    [
                        ["subcomponent_in", ["B"]],
                        [
                            "over",
                            "rest",
                            ["popularity_contest"]
                        ]
                    ]
                ]
            ],
            ["flatten"],
            ["limit_layers", 5]
        ]

        result = list(pipe(pipeline, make_test_graph()))

        # print(list(map(lambda g: g.vs["name"], result)))

        expected_graph_args = [
            # "B"" separated from the rest by "split_paths" and
            # "subcomponent_in' stages.
            ([], ["B"]),
            # Deps of "B", split into individual layers by "popularity_contest",
            # with "F" being most popular
            ([], ["F"]),
            ([], ["D"]),
            ([], ["E"]),
            # "rest" output of "split_paths" stage with "G" merged into it by
            # "limit_layers" stage.
            (
                [
                    ("Root1", "A"),
                    ("A", "C"),
                    ("Root3", "C"),
                ],
                ["Root2", "G"]
            )
        ]

        for (index, expected_graph_arg) in enumerate(expected_graph_args):

            self.assertGraphEqual(
                directed_graph(*expected_graph_arg),
                result[index]
            )
