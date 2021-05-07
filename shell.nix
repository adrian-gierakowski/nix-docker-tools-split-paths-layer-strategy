{ pkgs ? import ./nixpkgs.nix {}}:
let
  helpers = pkgs.callPackage (import ./helpers.nix) {};
in
  pkgs.mkShell {
    inputsFrom = [ (import ./default.nix { inherit pkgs; }) ];
    buildInputs = [
      helpers.format
      helpers.lint
      helpers.unittest
    ];
  }

