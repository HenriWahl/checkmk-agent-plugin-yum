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
    migrate from integer interval to float interval
    """
    if value is not None:
        # backward compatibility - migrate from deploy to deployment
        if value.get('deploy'):
            if value['deploy'].get('interval'):
                return {
                    'deployment': {
                        'deploy': {
                            'interval': float(value['deploy']['interval'])
                        }
                    }
                }
            else:
                return {
                    'deployment': {
                        'deploy': {
                            'interval': False
                        }
                    }
                }
        # fix a short time used interval instead of deploy
        elif value.get('interval'):
            return {
                'deployment': {
                    'deploy': {
                        'interval': float(value['interval'])
                    }
                }
            }
        # backward compatibility
        elif value.get('nointerval'):
            return {
                'deployment': {
                    'deploy': {
                        'interval': False
                    }
                }
            }
        else:
            return value
    else:
        return {
            'deployment': {
                'no_deploy': True
            }
        }


def _parameter_form_yum_bakery() -> Dictionary:
    """
    definition of the parameter form for the YUM bakery plugin
    :return:
    """
    return Dictionary(
        migrate=_migrate_int_to_float,
        title=Title('YUM/DNF Update Check'),
        help_text=Help('This will deploy the agent plugin <tt>YUM/DNF</tt>. This will activate the '
                       'check <tt>YUM/DNF</tt> on RedHat based hosts and monitor pending normal and security updates.'
                       ),
        elements={
            'deployment': DictElement(
                required=True,
                parameter_form=CascadingSingleChoice(
                    title=Title('Deployment options for the YUM/DNF Update Check'),
                    prefill=DefaultValue('deploy'),
                    help_text=Help(
                        'Determines how the the <tt>YUM/DNF</tt> plugin will run on a deployed agent or disables it on an deployed agent'),
                    elements=[
                        CascadingSingleChoiceElement(
                            name='deploy',
                            title=Title("Deploy the YUM/DNF Update Check"),
                            parameter_form=Dictionary(
                                title=Title('YUM/DNF Update Check'),
                                help_text=Help('This will deploy the agent plugin <tt>Yum</tt>. This will activate the '
                                               'check <tt>YUM/DNF</tt> on RedHat based hosts and monitor pending normal and security updates.'
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
                                            prefill=DefaultValue(DEFAULT_INTERVAL),
                                        )
                                    )
                                }
                            ),
                        ),
                        CascadingSingleChoiceElement(
                            name='no_deploy',
                            title=Title("Do not deploy the YUM/DNF Update Check"),
                            parameter_form=FixedValue(value=False),
                        )
                    ]
                ),
            ),
        },
    )


rule_spec_yum_bakery = AgentConfig(
    title=Title('YUM/DNF Update Check'),
    name='yum',
    parameter_form=_parameter_form_yum_bakery,
    # topic=Topic.APPLICATIONS,
    topic=Topic.OPERATING_SYSTEM,
    help_text=Help('This will deploy the agent plugin <tt>YUM/DNF</tt> '
                   'for checking package update status.'),
)
