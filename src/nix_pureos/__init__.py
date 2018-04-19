import os
import os.path
import subprocess
from copy import copy
from tempfile import TemporaryDirectory

import click
from nix_pureos.generation import Generations
from nix_pureos.paths import (APPLICATIONS_USER_DIR, CONFIG_DIR,
                              CONFIGURATION_NIX, GENERATIONS_DIR,
                              SYSTEMD_USER_DIR)
from nix_pureos.systemd import (SystemdSession, systemctl_preset_all,
                                systemd_daemon_reload)

HERE = os.path.dirname(__file__)

def systemd_switch_handler(old_profile, new_profile):

    def file_content(path):
        with open(path) as f:
            return f.read()
    
    systemd_session = SystemdSession()
    old_units = set(map(
        lambda x: systemd_session.get_unit(x),
        filter(
            lambda x: x.endswith('.service'),
            os.listdir(old_profile)
        )
    ))
    new_units = set(map(
        lambda x: systemd_session.get_unit(x),
        filter(
            lambda x: x.endswith('.service'),
            os.listdir(new_profile)
        )
    ))

    units_to_stop = old_units - new_units
    for unit in units_to_stop:
        unit.stop()

    systemd_daemon_reload()

    units_to_start = new_units - old_units
    for unit in units_to_start:
        unit.start()

    units_to_restart = old_units & new_units
    for unit in units_to_restart:
        old_unit_content = file_content(
            os.path.join(old_profile, unit.name)
        )

        new_unit_content = file_content(
            os.path.join(new_profile, unit.name)
        )

        if old_unit_content == new_unit_content:
            unit.ensure_started()
        else:
            unit.restart()

    systemctl_preset_all()


def ensure_config_dirs_present():
    for directory in [ CONFIG_DIR, GENERATIONS_DIR, APPLICATIONS_USER_DIR ]:
        os.makedirs(directory, exist_ok=True)


def nix_env():
    build_env = copy(os.environ)
    build_env['NIX_PATH'] = build_env['NIX_PATH'] + ':nix-pureos=' + CONFIGURATION_NIX
    return build_env


def nix_file():
    return os.path.join(
        HERE,
        'nix/modules.nix'
    )


def build_configuration_component(filename, component):
    print("Build configuration component '{component}' to file '{filename}'".format(
        component=component,
        filename=filename,
    ))
    subprocess.run(
        ['nix', 'build', '-f', nix_file(), '--show-trace', '-o', filename, component],
        env=nix_env(),
    )
    

def build_systemd_services(
        filename,
):
    build_configuration_component(filename, 'systemd-services')

    
def build_desktop_icons(
        filename
):
    build_configuration_component(filename, 'desktop-items')
    

def get_generation_service_files(path):
    return (
        list(map(
            lambda x: path + '/' + x,
            filter(
                lambda x: x.endswith('.service'),
                os.listdir(path)
            )
        ))
        if path is not None
        else []
    )


def install_packages():
    subprocess.run(
        ['nix-env', '-f', nix_file(), '-iA', 'packages'],
        env=nix_env()
    )

@click.command('nix-pureos')
@click.option('--collect-garbage',
              is_flag=True,
)
def main(collect_garbage):
    ensure_config_dirs_present()

    systemd_generations = Generations('nix-pureos-systemd', systemd_switch_handler)
    systemd_generations.create_new_generation(build_systemd_services)
    systemd_generations.install_current_generation(SYSTEMD_USER_DIR)

    desktop_items_generations = Generations('nix-pureos-desktop-icons')
    desktop_items_generations.create_new_generation(build_desktop_icons);
    desktop_items_generations.install_current_generation(APPLICATIONS_USER_DIR);

    install_packages()

    if collect_garbage:
        systemd_generations.delete_old_generations()
        desktop_items_generations.delete_old_generations()

if __name__ == '__main__':
    main()
