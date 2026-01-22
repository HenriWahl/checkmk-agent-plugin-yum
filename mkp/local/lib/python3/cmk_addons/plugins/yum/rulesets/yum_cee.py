#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
from collections.abc import Mapping

from cmk.rulesets.v1 import (
    Help,
    Label,
    Title,
)

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
    String
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
        title=Title('YUM package update check'),
        help_text=Help('This will deploy the agent plugin <tt>Yum</tt>. This will activate the '
                       'check <tt>YUM</tt> on RedHat based hosts and monitor pending normal and security updates.'
                       ),
        elements={
            'interval': DictElement(
                parameter_form=TimeSpan(
                    title=Title('Run asynchronously'),
                    label=Label('Interval for collecting data'),
                    help_text=Help(
                        'Determines how often the plugin will run on a deployed agent.'),
                    displayed_magnitudes=[TimeMagnitude.SECOND,
                                          TimeMagnitude.MINUTE,
                                          TimeMagnitude.HOUR,
                                          TimeMagnitude.DAY],
                    prefill=DefaultValue(60),
                )
            )
        },
    )


rule_spec_yum_bakery = AgentConfig(
    title=Title('YUM plugin'),
    name='yum',
    parameter_form=_parameter_form_yum_bakery,
    topic=Topic.APPLICATIONS,
    help_text=Help('This will deploy the agent plugin <tt>YUM</tt> '
                   'for checking patch status.'),
)
