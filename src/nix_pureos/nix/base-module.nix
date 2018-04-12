{ lib, ...
}:
let

serviceCfg = with lib; with lib.types;{
  "enable" = mkOption {
    type = bool;
    default = true;
  };
  "name" = mkOption {
    type = str;
  };
  "type" = mkOption {
    type = enum [ "forking" "simple" "notify" ];
    default = "simple";
  };
  "execStart" = mkOption {
    type = str;
  };
  "execStop" = mkOption {
    type = str;
    default = "";
  };
  "environment" = mkOption {
    type = attrsOf str;
    default = {};
  };
};

desktopFilesCfg = with lib; with types; {
  "name" = mkOption {
    type = str;
  };
  "exec" = mkOption {
    type = str;
  };
  "icon" = mkOption {
    type = str;
  };
  "type" = mkOption {
    type = enum [ "Application" ];
  };
  "terminal" = mkOption {
    type = bool;
  };
};

in
{
  options = {
    systemd = with lib.types; lib.mkOption {
      default = {};
      type = attrsOf (
        submodule {
          options = serviceCfg;
        }
      );
    };
    desktopFiles = lib.mkOption {
      default = {};
      type = lib.types.attrsOf (
        lib.types.submodule { options = desktopFilesCfg; }
      );
    };
  };
  config = {
    _module.args = {
      pkgs = import <nixpkgs> {};
    };
  };
}
