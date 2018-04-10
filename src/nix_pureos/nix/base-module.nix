{ lib, ...}:
let
  serviceCfg = with lib; with lib.types; {
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
in
{
  options.systemd = with lib.types; lib.mkOption {
    default = {};
    type = attrsOf (
      submodule {
        options = serviceCfg;
      }
    );
  };
  config = {
    _module.args = {
      pkgs = import <nixpkgs> {};
    };
  };
}
