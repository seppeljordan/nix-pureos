{ writeTextFile, jinja2-cli, _items, lib, stdenv }:
let

template = ./app.desktop.j2;

items = lib.mapAttrsToList
  (name: value: value // { _name = name; })
  _items;

generateItem = item:
  let configFile = writeTextFile{name =  "desktop-config"; text = (builtins.toJSON item); }; in
  ''
    ${jinja2-cli}/bin/jinja2 \
      --format=json \
      --strict \
      ${template} \
      ${configFile} \
      > ${item._name}.desktop
  '';

in

stdenv.mkDerivation {
  name = "desktop-applications";
  phases = [ "createOutputDirPhase" "buildPhase" ];
  createOutputDirPhase = ''
    mkdir -p $out
  '';
  buildPhase = ''
    pushd $out
    ${lib.concatMapStringsSep "\n" generateItem items}
    popd
  '';
}
