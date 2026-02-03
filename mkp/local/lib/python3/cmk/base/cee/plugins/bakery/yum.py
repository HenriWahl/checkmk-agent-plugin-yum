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

    # default to no interval - will be filled if set in config
    interval = None
    deploy_plugin = False

    if isinstance(conf, dict):
        deploy = conf.get('deploy')
        if deploy is None:
            if isinstance(conf.get('interval'), dict):
                try:
                    interval = int(conf.get('interval'))
                except (TypeError, ValueError):
                    interval = None
                deploy_plugin = True

        if isinstance(deploy, dict):
            interval = deploy.get('interval')
            if interval is not None:
                try:
                    interval = int(interval)
                except (TypeError, ValueError):
                    interval = None
            deploy_plugin = True

        if deploy_plugin:
            # only makes sense on Linux so just create for that OS
            yield Plugin(
                base_os=OS.LINUX,
                source=Path('yum'),
                interval=interval
            )


# register the bakery plugin with its arguments
register.bakery_plugin(
    name='yum',
    files_function=get_yum_files
)
