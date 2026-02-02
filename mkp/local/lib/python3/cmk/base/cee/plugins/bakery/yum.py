#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from pathlib import Path
from typing import Any

from cmk.base.cee.plugins.bakery.bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_yum_files(conf: Any) -> FileGenerator:
    """
    Simple bakery plugin generator for yum

    conf looks like: {'deployment': ('deploy', {'interval': 18060.0})}
    mind the tuple!
    """

    # debugging
    with open('/tmp/debug.txt', 'a') as debug_file:
        debug_file.write(f'config: {conf}\n')

    if isinstance(conf, dict):
        # default to no interval - will be filled if set in config
        interval = None

        # new config structure since version 2.6.0 of the plugin
        if conf.get('deployment'):
            if 'deploy' in conf['deployment']:
                # this is a tuple ('deploy', { ... })
                deploy = conf['deployment'][1]
                if isinstance(deploy, dict) and \
                        deploy.get('interval'):
                    interval = int(deploy['interval'])
            elif 'no_deploy' in conf['deployment']:
                return

        # backward compatibility - check older config options
        else:
            if conf.get('interval') is not None:
                interval = conf.get('interval')
            elif conf.get('deploy', 'interval')[1] is not None:
                interval = conf.get('deploy', 'interval')[1]

    # only makes sense on Linux so just create for that OS
    yield Plugin(base_os=OS.LINUX,
                 source=Path('yum'),
                 interval=interval
                 )


# register the bakery plugin with its arguments
register.bakery_plugin(
    name='yum',
    files_function=get_yum_files
)
