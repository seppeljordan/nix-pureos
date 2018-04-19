import os
from distutils.core import setup

setup(
    name='nix-pureos',
    description='Manage user services and files with nix on pureOS',
    author='Sebastian Jordan',
    author_email='sebastian.jordan.mail@googlemail.com',
    license='GPLv3',
    version='1.0',
    install_requires=[
        'click',
        'pydbus',
        'xdg',
    ],
    package_dir={'': 'src'},
    packages=[
        'nix_pureos'
    ],
    entry_points={
        'console_scripts': [
            'nix-pureos = nix_pureos:main',
        ],
    },
    data_files=[
        ('nix', list(map(
            lambda x: os.path.join('src/nix_pureos/nix', x),
            [
                'base-module.nix',
                'modules.nix',
                'systemd.nix',
                'service.j2',
                'app.desktop.j2',
                'desktop.nix',
            ]
        )))
    ],
    include_package_data=True,
)
