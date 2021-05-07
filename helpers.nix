{
  bash,
  lib,
  makeWrapper,
  runCommandNoCCLocal,
  writers
}:
let
  mkScriptBinWithDeps = interpreter: deps: name: content:
    let
      scriptNoDeps = writers.makeScriptWriter
        {
          inherit interpreter;
          # This should work with most shell interpreters.
          check = "${interpreter} -n $1";
        }
        "${name}-no-deps"
        content
      ;
    in runCommandNoCCLocal name { buildInputs = [ makeWrapper ]; } ''
      mkdir -p $out/bin
      binPath=$out/bin/${name}
      makeWrapper ${scriptNoDeps} $out/bin/${name} --prefix PATH : ${lib.makeBinPath deps}
    '';
in {
  inherit mkScriptBinWithDeps;
  mkBashScriptBinWithDeps = mkScriptBinWithDeps "${bash}/bin/bash";
}

