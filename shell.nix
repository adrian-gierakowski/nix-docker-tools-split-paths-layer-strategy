{ pkgs ? import ./nixpkgs.nix {}}:
  pkgs.mkShell {
    inputsFrom = [ (import ./default.nix { inherit pkgs; }) ];
    buildInputs = [
      pkgs.python39Packages.autopep8
      pkgs.nodePackages.nodemon
    ];
  }

