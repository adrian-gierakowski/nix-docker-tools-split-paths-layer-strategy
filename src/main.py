import json as json
import sys as sys

from .lib import debug, load_json
from .flatten_references_graph import flatten_references_graph


def main_impl(file_path):
    debug(f"loading json from {file_path}")

    data = load_json(file_path)

    references_graph = data["graph"]
    pipeline = data["pipeline"]

    debug("references_graph", references_graph)
    debug("pipeline", pipeline)

    result = flatten_references_graph(references_graph, pipeline)

    debug("result", result)

    return json.dumps(
        result,
        # For reproducibility.
        sort_keys=True,
        indent=2,
        # Avoid training whitespaces.
        separators=(",", ": ")
    )


def main():
    file_path = sys.argv[1]
    print(main_impl(file_path))


if __name__ == "__main__":
    main()
