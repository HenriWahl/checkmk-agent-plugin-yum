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
        else:
            return {'interval': DEFAULT_INTERVAL}
    # new simpler interval form
    elif value.get('interval'):
        return {'interval': float(value['interval'])}
    else:
        return value


def _parameter_form_yum_bakery_new() -> Dictionary:
    """
    definition of the parameter form for the YUM bakery plugin
    :return:
    """
    return Dictionary(
        # migrate=_migrate_int_to_float,
        title=Title('YUM package update check'),
        # help_text=Help('This will deploy the agent plugin <tt>Yum</tt>. This will activate the '
        #                'check <tt>YUM</tt> on RedHat based hosts and monitor pending normal and security updates.'
        #                ),
        elements={
            'deploy': DictElement(
                required=True,
                parameter_form=CascadingSingleChoice(
                    title=Title('CascadingSingleChoice Deployment options for the Yum plugin.'),
                    # prefill=DefaultValue("interval"),
                    # help_text=Help(
                    #     'Determines how the the <tt>Yum</tt> plugin will run on a deployed agent or disables it on an deployed agent'),
                    elements=[

                    ]
                )
            ),
            'interval': DictElement(
                parameter_form=TimeSpan(
                    title=Title('Custom execution interval'),
                    label=Label('Interval for collecting data'),
                    # help_text=Help(
                    #     'Determines how often the plugin will run on a deployed agent.'),
                    displayed_magnitudes=[TimeMagnitude.SECOND,
                                          TimeMagnitude.MINUTE,
                                          TimeMagnitude.HOUR,
                                          TimeMagnitude.DAY],
                    prefill=DefaultValue(DEFAULT_INTERVAL),
                )
            )
        },
    )


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
        # help_text=Help('This will deploy the agent plugin <tt>Yum</tt>. This will activate the '
        #                'check <tt>Yum</tt> on redHat based hosts and monitor pending normal and security updates.'
        #                ),
        elements={
            "deploy": DictElement(
                required=True,
                parameter_form=CascadingSingleChoice(
                    title=Title('CascadingSingleChoice Deployment options for the Yum plugin.'),
                    # prefill=DefaultValue("interval"),
                    # help_text=Help(
                    #     'Determines how the the <tt>Yum</tt> plugin will run on a deployed agent or disables it on an deployed agent'),
                    elements=[
                        CascadingSingleChoiceElement(
                            name='interval_1',
                            title=Title('interval_1'),
                            parameter_form=Dictionary(
                                title=Title('Dictionary YUM package update check'),
                                # help_text=Help('This will deploy the agent plugin <tt>Yum</tt>. This will activate the '
                                #                'check <tt>YUM</tt> on RedHat based hosts and monitor pending normal and security updates.'
                                #                ),
                                elements={
                                    'interval_2': DictElement(
                                        parameter_form=TimeSpan(
                                            title=Title('Run asynchronously'),
                                            label=Label('Interval for collecting data'),
                                            # help_text=Help(
                                            #     'Determines how often the plugin will run on a deployed agent.'),
                                            displayed_magnitudes=[TimeMagnitude.SECOND,
                                                                  TimeMagnitude.MINUTE,
                                                                  TimeMagnitude.HOUR,
                                                                  TimeMagnitude.DAY],
                                            prefill=DefaultValue(DEFAULT_INTERVAL),
                                        )
                                    )
                                },
                            )
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
    topic=Topic.GENERAL,
    # help_text=Help('This will deploy the agent plugin <tt>YUM</tt> '
    #                'for checking package update status.'),
)
