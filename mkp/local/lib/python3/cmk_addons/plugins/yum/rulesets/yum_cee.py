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


# default interval in seconds
DEFAULT_INTERVAL = 60.0


def _migrate_int_to_float(value: object) -> Mapping[str, object]:
    """
    migrate from deploy to interval and from integer interval to float interval
    """
    # backward compatibility - migrate from deploy to interval
    if value.get('deploy'):
        if value['deploy'].get('interval'):
            return {'interval': float(value['deploy']['interval'])}
    # new simpler interval form
    elif value.get('interval'):
        return {'interval': float(value['interval'])}
    else:
        return {'interval': DEFAULT_INTERVAL}


def _parameter_form_yum_bakery() -> Dictionary:
    """
    definition of the parameter form for the YUM bakery plugin
    :return:
    """
    return Dictionary(
        migrate=_migrate_int_to_float,
        title=Title('YUM package update check'),
        help_text=Help('This will deploy the agent plugin <tt>Yum</tt>. This will activate the '
                       'check <tt>YUM</tt> on RedHat based hosts and monitor pending normal and security updates.'
                       ),
        elements={
            'interval': DictElement(
                parameter_form=TimeSpan(
                    title=Title('Custom execution interval'),
                    label=Label('Interval for collecting data'),
                    help_text=Help(
                        'Determines how often the plugin will run on a deployed agent.'),
                    displayed_magnitudes=[TimeMagnitude.SECOND,
                                          TimeMagnitude.MINUTE,
                                          TimeMagnitude.HOUR,
                                          TimeMagnitude.DAY],
                    prefill=DefaultValue(DEFAULT_INTERVAL),
                )
            )
        },
    )


rule_spec_yum_bakery = AgentConfig(
    title=Title('YUM plugin'),
    name='yum',
    parameter_form=_parameter_form_yum_bakery,
    topic=Topic.GENERAL,
    help_text=Help('This will deploy the agent plugin <tt>YUM</tt> '
                   'for checking package update status.'),
)
