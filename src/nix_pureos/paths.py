import os

from xdg import XDG_CONFIG_HOME, XDG_DATA_HOME


CONFIG_DIR=XDG_CONFIG_HOME + '/nix-pureos'
SYSTEMD_USER_DIR=XDG_CONFIG_HOME + '/systemd/user'
CONFIGURATION_NIX=os.path.join(
    CONFIG_DIR,
    'configuration.nix'
)
APPLICATIONS_USER_DIR=os.path.join(
    XDG_DATA_HOME, 'applications/nix-pureos'
)
GENERATIONS_DIR=CONFIG_DIR + '/generations'
