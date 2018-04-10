let
  nixpkgs = import <nixpkgs> {};
  modules = nixpkgs.lib.evalModules {
    modules = [
      (import ./base-module.nix)
      (import <nix-pureos>)
    ];
  };
  systemd = services: nixpkgs.callPackages ./systemd.nix {
    jinja2-cli = nixpkgs.pypiPackages3.packages.jinja2-cli;
    services = services;
  };
in
{
  systemd-services = systemd modules.config.systemd;
}
