import subprocess


from pydbus import SessionBus


class SystemdSession(object):
    def __init__(self):
        self.session_bus = SessionBus()
        self.systemd = self.session_bus.get('org.freedesktop.systemd1')

    def get_unit(self, name):
        unit_object = self.systemd.LoadUnit(name)
        return SystemdUnit(
            name,
            self.session_bus.get('.systemd1', unit_object),
            self.systemd
        )


class SystemdUnit(object):
    def __init__(self, name, dbus_object, systemd_session):
        self.dbus_object = dbus_object
        self.name = name
        self.systemd = systemd_session

    def start(self):
        print('Start unit "{name}"'.format(name=self.name))
        self.dbus_object.Start("fail")

    def stop(self):
        print('Stop unit "{name}"'.format(name=self.name))
        self.dbus_object.Stop("fail")

    def restart(self):
        print('Restart unit "{name}"'.format(name=self.name))
        self.systemd.RestartUnit(self.name, "fail")

    def is_active(self):
        return 'active' == self.dbus_object.Get('org.freedesktop.systemd1.Unit', 'ActiveState')

    def ensure_started(self):
        if not self.is_active():
            self.start()

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


def systemd_daemon_reload():
    subprocess.run(['systemctl', '--user', 'daemon-reload'])


def systemctl_preset_all():
    subprocess.run(['systemctl', '--user', 'preset-all'])
    

