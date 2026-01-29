#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
from collections.abc import Mapping

from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    DefaultValue,
#    SingleChoice,
#    SingleChoiceElement,
#    Integer,
#    InputHint,
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    FixedValue,
    TimeSpan,
    TimeMagnitude,
#    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic, Title, Help

# Default interval in seconds
DEFAULT_INTERVAL = 60.0

def _migrateInt(value: object) -> Mapping[str, object]:
  """
  Migrate old config formats to new nested structure.
  Handles backward compatibility for:
  - {'interval': value} - old format with interval only
  - {'deploy': ('interval', value)} - intermediate format
  - {'deploy': ('nointerval', None)} - intermediate format for no deployment
  - {'deploy': ('deploy', {...})} - new format (already migrated)
  """
  if value is not None:
    # Ensure value is a dictionary
    if not isinstance(value, dict):
      return {'deploy': ('nointerval', None)}
    
    # Handle old format: {'interval': value}
    if 'interval' in value and 'deploy' not in value:
      interval_value = value["interval"]
      if interval_value is not None and interval_value >= 0:
        return {'deploy': ('deploy', {'interval': float(interval_value)})}
      else:
        # No interval specified, deploy without interval
        return {'deploy': ('deploy', {})}
    # Handle intermediate and new formats with 'deploy' key
    elif 'deploy' in value and isinstance(value['deploy'], tuple):
      deploy_choice, deploy_value = value['deploy']
      if deploy_choice == 'interval':
        # Intermediate format: migrate to new format
        return {'deploy': ('deploy', {'interval': float(deploy_value)})}
      elif deploy_choice == 'nointerval':
        # Already correct format
        return {'deploy': ('nointerval', None)}
      elif deploy_choice == 'deploy':
        # Already in new format - no migration needed
        return value
    # Already in new format or unknown format - return as is
    else:
      return value
  # No value means don't deploy
  else:
    return {'deploy': ('nointerval', None)}


def _parameter_form_yum_bakery() -> Dictionary:
    return Dictionary(
        migrate=_migrateInt,
        title=Title('Deploy the Yum plugin'),
        help_text=Help('This will deploy the agent plugin <tt>Yum</tt>. This will activate the '
                       'check <tt>Yum</tt> on RedHat based hosts and monitor pending normal and security updates.'
        ),
        elements={
          "deploy": DictElement(
            required=True,
            parameter_form=CascadingSingleChoice(
              title=Title('Deployment options for the Yum plugin'),
              prefill=DefaultValue("deploy"),
              help_text=Help('Determines how the <tt>Yum</tt> plugin will run on a deployed agent or disables it on a deployed agent'),
              elements=[
                CascadingSingleChoiceElement(
                  name="deploy",
                  title=Title("Deploy the Yum plugin"),
                  parameter_form=Dictionary(
                    title=Title('Yum plugin configuration'),
                    help_text=Help('Configure how the <tt>Yum</tt> plugin will run on the deployed agent.'),
                    elements={
                      "interval": DictElement(
                        required=False,
                        parameter_form=TimeSpan(
                          title=Title('Run asynchronously'),
                          help_text=Help('Determines how often the <tt>Yum</tt> plugin will run on a deployed agent. '
                                       'If not set, the plugin will run synchronously with each agent execution.'),
                          displayed_magnitudes=[TimeMagnitude.SECOND, TimeMagnitude.MINUTE, TimeMagnitude.HOUR, TimeMagnitude.DAY],
                          prefill=DefaultValue(DEFAULT_INTERVAL),
                        ),
                      ),
                    },
                  ),
                ),
                CascadingSingleChoiceElement(
                  name="nointerval",
                  title=Title("Do not deploy the Yum plugin"),
                  parameter_form=FixedValue(value=None),
                )
              ]
            ),
          ),
        },
      )


rule_spec_yum_bakery = AgentConfig(
    title=Title('YUM plugin'),
    name='yum',
    parameter_form=_parameter_form_yum_bakery,
    topic=Topic.APPLICATIONS,
    help_text=Help('This will deploy the agent plugin <tt>Yum</tt> '
                   'for checking patch status.'),
)
