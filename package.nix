{
  callPackage,
  gwenview,
  nix-gitignore,
  python39Packages,
}:
let
  pythonPackages = python39Packages;
  inherit (callPackage (import ./helpers.nix) {}) mkBashScriptBinWithDeps;
  # helpers = callPackage (import ./helpers.nix) {};
  # inherit () mkBashScriptBinWithDeps;
  unittest = mkBashScriptBinWithDeps [pythonPackages.python] "unittest" ./src/unittest.sh;
  lint = mkBashScriptBinWithDeps [pythonPackages.flake8] "lint" ./src/lint.sh;
in pythonPackages.buildPythonApplication {
  version = "0.1.0";
  pname = "flatten-references-graph";

  # Note this uses only ./src/.gitignore
  src = nix-gitignore.gitignoreSource [] ./src;

  # Specify runtime dependencies for the package
  propagatedBuildInputs = with pythonPackages; [
    python-igraph
    toolz
  ];

  doCheck = true;
  checkInputs = [
    lint
    unittest
  ];
  checkPhase = ''
    lint
    unittest
  '';
}
