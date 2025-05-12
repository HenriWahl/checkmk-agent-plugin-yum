#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from pathlib import Path
from typing import Any

from cmk.base.cee.plugins.bakery.bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_yum_files(conf: Any) -> FileGenerator:
#    if conf.get('deploy', 'nointerval') == 'nointerval':
#      return
  if conf.get('interval') is not None:
    interval=conf.get('interval')
  elif conf.get('deploy', 'interval')[1] is not None:
    interval=conf.get('deploy', 'interval')[1]

  yield Plugin(base_os=OS.LINUX,
               source=Path('yum'),
               interval=int(interval)
  )

register.bakery_plugin(
    name='yum',
    files_function=get_yum_files,
)
