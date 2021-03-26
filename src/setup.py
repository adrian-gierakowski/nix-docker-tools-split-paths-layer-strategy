from distutils.core import setup

setup(
    name="flatten_references_graph",
    version="0.1.0",
    author="Adrian Gierakowski",
    entry_points={
        "console_scripts": [
            "flatten_references_graph=fflatten_references_graph.main:main"
        ]
    }
)
