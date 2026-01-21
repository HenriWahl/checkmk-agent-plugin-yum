#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
from collections.abc import Mapping

from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
#    DefaultValue,
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

def _migrateInt(value: object) -> Mapping[str, object]:
  if value is not None:
    if 'interval' in value:
      match value["interval"]:
        case _ if value["interval"] >= 0:
          return {'deploy': ('interval', float(value["interval"]))}
        case None:
          return {'deploy': ('interval', 77.0)}
    else:
      return value
  else:
    return {'deploy': 'nointerval'}


def _parameter_form_yum_bakery() -> Dictionary:
    return Dictionary(
        migrate=_migrateInt,
        title=Title('Deploy the Yum plugin'),
        help_text=Help('This will deploy the agent plugin <tt>Yum</tt>. This will activate the '
                       'check <tt>Yum</tt> on redHat based hosts and monitor pending normal and security updates.'
        ),
        elements={
          "deploy": DictElement(
            required=True,
            parameter_form=CascadingSingleChoice(
              title=Title('Deployment options for the Yum plugin.'),
              #prefill=DefaultValue("interval"),
              help_text=Help('Determines how the the <tt>Yum</tt> plugin will run on a deployed agent or disables it on an deployed agent'),
              elements=[
                CascadingSingleChoiceElement(
                  name="interval",
                  title=Title("Deploy the Yum plugin"),
                  parameter_form=TimeSpan(
                    title=Title('Interval that the plugin runs at on the client'),
                    help_text=Help('Determines how often that the <tt>Yum</tt> plugin will run on a deployed agent.'),
                    displayed_magnitudes=[TimeMagnitude.SECOND, TimeMagnitude.MINUTE, TimeMagnitude.HOUR, TimeMagnitude.DAY],
                    #prefill=DefaultValue(129600.0),
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
