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
    shellHook = ''
      echo '
      **********************************************************************
      **********************************************************************

        Commands useful for development (should be executed from scr dir):


        format
          - formats all files in place using autopep8

        lint
          - lints all files using flake8

        unittest
          - runs all unit tests

      **********************************************************************
      **********************************************************************
      '
    '';
  }

