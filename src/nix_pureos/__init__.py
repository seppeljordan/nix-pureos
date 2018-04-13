import os
import os.path
import subprocess
from copy import copy
from tempfile import TemporaryDirectory

from xdg import XDG_CONFIG_HOME, XDG_DATA_HOME

HERE = os.path.dirname(__file__)
CONFIG_DIR=XDG_CONFIG_HOME + '/nix-pureos'
SYSTEMD_USER_DIR=XDG_CONFIG_HOME + '/systemd/user'
GENERATIONS_DIR=CONFIG_DIR + '/generations'
CONFIGURATION_NIX=os.path.join(
    CONFIG_DIR,
    'configuration.nix'
)
APPLICATIONS_USER_DIR=os.path.join(
    XDG_DATA_HOME, 'applications/nix-pureos'
)


def no_handler(old, new):
    pass


class Generations(object):
    def __init__(self, generation_prefix, generation_switch_handler=no_handler):
        self.current_generation = None
        self.generation_prefix = generation_prefix + '-'
        self.generation_switch_handler = generation_switch_handler
        generations_files = self.get_sorted_generation_files()
        if len(generations_files) > 0:
            latest_generation_file = generations_files[-1]
            self.current_generation = int(latest_generation_file.replace(
                self.generation_prefix,
                ''
            ))

    def is_generation_file(self, path):
        return path.startswith(GENERATIONS_DIR + '/' + self.generation_prefix)

    def unlink_files(self, installation_dir):
        installation_contents = map(
            lambda x: installation_dir + '/' + x,
            os.listdir(installation_dir)
        )
        installation_symlinks = filter(
            lambda p: os.path.islink(p) and self.is_generation_file(os.readlink(p)),
            installation_contents
        )
        for path in installation_symlinks:
            absolute_path = os.path.join(installation_dir, path)
            os.remove(absolute_path)

    def link_files(self, installation_dir, generation_number):
        generation_path = self.get_generation_path(generation_number)
        generation_files = os.listdir(generation_path)
        for path in generation_files:
            os.symlink(
                os.path.join(generation_path, path),
                os.path.join(installation_dir, path)
            )


    def install_current_generation(self, installation_dir):
        self.unlink_files(installation_dir)
        self.link_files(installation_dir, self.current_generation)
        self.generation_switch_handler(
            self.get_last_generation_path(),
            self.get_current_generation_path()
        )

    def get_sorted_generation_files(self):
        return list(
            sorted(
                filter(
                    lambda file: file.startswith(self.generation_prefix),
                    os.listdir(GENERATIONS_DIR)
                ),
                key=lambda x: int(x.replace(self.generation_prefix, '')),
            )
        )

    def create_new_generation(self, file_generator):
        """file_generator is a function that only takes one argument: a path"""
        next_generation = self.current_generation + 1 if self.current_generation is not None else 0
        next_generation_filename = GENERATIONS_DIR + '/' + self.generation_prefix + str(next_generation)
        file_generator(next_generation_filename)
        self.current_generation = next_generation

        return next_generation_filename

    def get_generation_path(self, n):
        return GENERATIONS_DIR + '/' + self.generation_prefix + str(n)

    def get_last_generation_path(self):
        generation_files = self.get_sorted_generation_files()
        if len(generation_files) < 2:
            return None
        else:
            return GENERATIONS_DIR + '/' + generation_files[-2]

    def get_current_generation_path(self):
        generation_files = self.get_sorted_generation_files()
        if len(generation_files) < 1:
            return None
        else:
            return GENERATIONS_DIR + '/' + generation_files[-1]


def start_unit(unit):
    subprocess.run(['systemctl', '--user', 'start', unit])


def stop_unit(unit):
    subprocess.run(['systemctl', '--user', 'stop', unit])


def restart_unit(unit):
    subprocess.run(['systemctl', '--user', 'restart', unit])


def daemon_reload():
    subprocess.run(['systemctl', '--user', 'daemon-reload'])


def systemctl_preset_all():
    subprocess.run(['systemctl', '--user', 'preset-all'])
    

def systemd_switch_handler(old_profile, new_profile):
    old_units = set(filter(
        lambda x: x.endswith('.service'),
        os.listdir(old_profile)
    ))
    new_units = set(filter(
        lambda x: x.endswith('.service'),
        os.listdir(new_profile)
    ))

    units_to_stop = old_units - new_units
    for unit in units_to_stop:
        stop_unit(unit)

    daemon_reload()

    units_to_start = new_units - old_units
    for unit in units_to_start:
        start_unit(unit)

    units_to_restart = old_units & new_units
    for unit in units_to_restart:
        restart_unit(unit)

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
    print("Build configuration component {component} to file '{filename}'".format(
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

def main():
    ensure_config_dirs_present()
    systemd_generations = Generations('nix-pureos-systemd', systemd_switch_handler)
    systemd_generations.create_new_generation(build_systemd_services)
    systemd_generations.install_current_generation(SYSTEMD_USER_DIR)

    desktop_items_generations = Generations('nix-pureos-desktop-icons')
    desktop_items_generations.create_new_generation(build_desktop_icons);
    desktop_items_generations.install_current_generation(APPLICATIONS_USER_DIR);

    install_packages()

if __name__ == '__main__':
    main()
