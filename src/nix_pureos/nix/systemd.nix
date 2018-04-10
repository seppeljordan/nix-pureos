{ stdenv, services, jinja2-cli, lib, writeTextFile }:
let template = ./service.j2;
    toList = xs: lib.mapAttrsToList (name: value: value) xs;
    generateMakeService = service:
      let
        configFile = writeTextFile {
          name = "service-config";
          text = (builtins.toJSON service);
        };
      in
      ''
        ${jinja2-cli}/bin/jinja2 \
          --format=json \
          --strict \
          ${template} \
          ${configFile} \
          > ${service.name}.service
      '';
  presets = lib.mapAttrsToList
    (name: value: "${if value.enable then "enable" else "disable"} ${name}.service")
    services;
  presets-file = writeTextFile {
    name = "systemd-user-presets";
    text = lib.concatStringsSep "\n" presets + "\ndisable *";
  };
in
stdenv.mkDerivation {
  name = "systemd-user-services";
  phases = [ "createOutputDirPhase" "buildPhase" "installPresetPhase" ];

  createOutputDirPhase = ''
    mkdir -p $out
  '';
  
  buildPhase = ''
    pushd $out
    ${lib.concatMapStringsSep "\n" generateMakeService (toList services)}
    popd
  '';

  installPresetPhase = ''
    pushd $out
    ln ${presets-file} user.preset
    popd
  '';
}
