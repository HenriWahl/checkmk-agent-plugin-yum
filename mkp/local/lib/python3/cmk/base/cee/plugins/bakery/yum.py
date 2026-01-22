#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from pathlib import Path
from typing import Any

from cmk.base.cee.plugins.bakery.bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_yum_files(conf: Any) -> FileGenerator:
    # when interval is set, convert to int, otherwise None is okay
    interval = conf.get('interval')
    if interval:
        interval = int(interval)

    yield Plugin(base_os=OS.LINUX,
                 source=Path('yum'),
                 interval=interval
                 )


register.bakery_plugin(
    name='yum',
    files_function=get_yum_files,
)
