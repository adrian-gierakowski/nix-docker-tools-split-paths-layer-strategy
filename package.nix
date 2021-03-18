{ gwenview, python3Packages }: python3Packages.buildPythonApplication {
  version = "0.0.1";
  pname = "split-paths-layer-strategy";

  src = ./src;

  # Specify runtime dependencies for the package
  buildInputs = with python3Packages; [
    python-igraph
    pycairo
    gwenview
  ];

  # Test dependencies
  checkInputs = with python3Packages; [
    flake8
  ];

  checkPhase = ''
    ${python3Packages.flake8}/bin/flake8 --show-source
  '';
}
