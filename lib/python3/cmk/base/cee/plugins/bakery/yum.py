#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from pathlib import Path
from typing import Any

from cmk.base.cee.plugins.bakery.bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_yum_files(conf: Any) -> FileGenerator:
  """
  Bakery plugin generator for yum.
  
  Handles multiple config formats for backward compatibility:
  - New format: {'deploy': ('deploy', {'interval': 60.0})} - deploy with optional interval
  - New format: {'deploy': ('deploy', {})} - deploy without interval (synchronous)
  - New format: {'deploy': ('nointerval', None)} - do not deploy
  - Old format: {'interval': 60} - deploy with interval
  - Old format: {'deploy': ('interval', 60)} - deploy with interval (intermediate format)
  """
  
  # Don't deploy if explicitly disabled
  if isinstance(conf, dict):
    if conf.get('deploy') == ('nointerval', None):
      return
    
    # Handle new nested format: {'deploy': ('deploy', {optional 'interval': value})}
    if conf.get('deploy') and isinstance(conf['deploy'], tuple):
      deploy_choice, deploy_config = conf['deploy']
      if deploy_choice == 'deploy':
        if isinstance(deploy_config, dict):
          # New format: interval is optional in the nested dictionary
          interval = deploy_config.get('interval')
          if interval is not None:
            interval = int(interval)
          yield Plugin(base_os=OS.LINUX,
                       source=Path('yum'),
                       interval=interval)
          return
        # Old intermediate format: {'deploy': ('interval', value)}
        elif deploy_choice == 'interval':
          interval = int(deploy_config)
          yield Plugin(base_os=OS.LINUX,
                       source=Path('yum'),
                       interval=interval)
          return
      elif deploy_choice == 'nointerval':
        return
    
    # Backward compatibility: old format {'interval': value}
    if 'interval' in conf:
      interval = conf.get('interval')
      if interval is not None:
        interval = int(interval)
      yield Plugin(base_os=OS.LINUX,
                   source=Path('yum'),
                   interval=interval)
      return

  # Default: deploy without interval (synchronous execution)
  yield Plugin(base_os=OS.LINUX,
               source=Path('yum'),
               interval=None)

register.bakery_plugin(
    name='yum',
    files_function=get_yum_files,
)
