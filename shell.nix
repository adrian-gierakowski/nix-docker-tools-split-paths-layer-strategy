{ pkgs ? import ./nixpkgs.nix {}}:
  pkgs.mkShell {
    inputsFrom = [ (import ./default.nix { inherit pkgs; }) ];
    buildInputs = [
      pkgs.nodePackages.nodemon
    ];
  }

