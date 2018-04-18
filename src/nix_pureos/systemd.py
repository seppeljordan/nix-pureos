import subprocess


class SystemdUnit(object):
    def __init__(self, name):
        self.name = name

    def start(self):
        subprocess.run(['systemctl', '--user', 'start', self.name])        

    def stop(self):
        subprocess.run(['systemctl', '--user', 'stop', self.name])

    def restart(self):
        subprocess.run(['systemctl', '--user', 'restart', self.name])

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


def systemd_daemon_reload():
    subprocess.run(['systemctl', '--user', 'daemon-reload'])


def systemctl_preset_all():
    subprocess.run(['systemctl', '--user', 'preset-all'])
    

