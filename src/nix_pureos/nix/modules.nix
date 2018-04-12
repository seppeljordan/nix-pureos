let

nixpkgs = import <nixpkgs> {};

modules = nixpkgs.lib.evalModules {
  modules = [
    (import ./base-module.nix)
    (import <nix-pureos>)
  ];
};

systemd = services: nixpkgs.callPackage ./systemd.nix {
  jinja2-cli = nixpkgs.pypiPackages3.packages.jinja2-cli;
  services = services;
};

desktopItems = items: nixpkgs.callPackage ./desktop.nix {
  jinja2-cli = nixpkgs.pypiPackages3.packages.jinja2-cli;
  _items = items;
};

in
{
  systemd-services = systemd modules.config.systemd;
  desktop-items = desktopItems modules.config.desktopFiles;
}
