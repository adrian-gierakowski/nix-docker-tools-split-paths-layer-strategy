{
  nix-gitignore,
  python39Packages,
  callPackage
}:
let
  pythonPackages = python39Packages;
  inherit (callPackage (import ./helpers.nix) {}) lint unittest;

in pythonPackages.buildPythonApplication {
  version = "0.1.0";
  pname = "flatten-references-graph";

  # Note this uses only ./src/.gitignore
  src = nix-gitignore.gitignoreSource [] ./src;

  propagatedBuildInputs = with pythonPackages; [
    python-igraph
    toolz
  ];

  doCheck = true;

  checkPhase = ''
    ${lint}/bin/lint
    ${unittest}/bin/unittest
  '';
}
