{ nix-gitignore, gwenview, python39Packages, }:
let
  pythonPackages = python39Packages;
in pythonPackages.buildPythonApplication {
  version = "0.1.0";
  pname = "flatten-references-graph";

  # Note this uses only ./src/.gitignore
  src = nix-gitignore.gitignoreSource [] ./src;

  # Specify runtime dependencies for the package
  propagatedBuildInputs = with pythonPackages; [
    python-igraph
  ];

  # Test dependencies
  checkInputs = with pythonPackages; [
    flake8
    pycairo
    gwenview
  ];

  doCheck = true;
  checkPhase = ''
    ${pythonPackages.flake8}/bin/flake8 --show-source
  '';
}
