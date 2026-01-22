#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from pathlib import Path
from typing import Any

from cmk.base.cee.plugins.bakery.bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_yum_files(conf: Any) -> FileGenerator:
    """
    Simple bakery plugin generator for yum
    """
    # when interval is set, convert to int, otherwise None is okay
    interval = conf.get('interval')
    if interval:
        interval = int(interval)

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
