import unittest
import inspect as inspect
from .main import main_impl
from .lib import path_relative_to_file

if __name__ == "__main__":
    unittest.main()


class TestMain(unittest.TestCase):

    def test_main_impl(self):
        file_path = path_relative_to_file(
            __file__,
            "__test_fixtures/flatten-references-graph-main-input.json"
        )

        result = main_impl(file_path)

        self.assertEqual(
            result,
            inspect.cleandoc(
                """
                [
                  [
                    "C"
                  ],
                  [
                    "A"
                  ],
                  [
                    "B"
                  ]
                ]
                """
            )
        )
