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

    # debugging
    with open('/tmp/debug-migrate_int_to_float.txt', 'a') as debug_file:
        debug_file.write(f'value: {value}\n')

    if value is not None:
        # backward compatibility - migrate from deploy to deployment
        if value.get('deploy'):
            if value['deploy'].get('interval'):
                return {
                    'deploy': {
                        'interval': float(value['deploy']['interval'])
                    }
                }
            else:

                with open('/tmp/debug-migrate_int_to_float-no-interval.txt', 'a') as debug_file:
                    debug_file.write(f'value: {value}\n')

                return {
                    'deploy': {
                        'interval': dict()
                    }
                }
        # fix a short time used interval instead of deploy
        elif value.get('interval'):
            return {
                'deploy': {
                    'interval': float(value['interval'])
                }
            }
        # backward compatibility
        elif value.get('nointerval'):
            return {
                'deploy': {
                    'interval': dict()
                }
            }
        else:
            return value
    else:
        return {
                'deploy': dict()
        }


def _parameter_form_yum_bakery() -> Dictionary:
    """
    definition of the parameter form for the YUM bakery plugin
    :return:
    """
    return Dictionary(
        migrate=_migrate_int_to_float,
        title=Title('YUM Update Check'),
        help_text=Help('This will deploy the agent plugin <tt>YUM</tt>. This will activate the '
                       'check <tt>YUM</tt> on RedHat based hosts and monitor pending normal and security updates.'
                       ),
        elements={
            'deploy': DictElement(
                parameter_form=Dictionary(
                    title=Title('Deploy plugin'),
                    help_text=Help(
                        'Determines how the the <tt>YUM</tt> plugin will run on a deployed agent or disables it on an deployed agent'),
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
            )
        }
    )


rule_spec_yum_bakery = AgentConfig(
    title=Title('YUM Update Check'),
    name='yum',
    parameter_form=_parameter_form_yum_bakery,
    topic=Topic.OPERATING_SYSTEM,
    help_text=Help('This will deploy the agent plugin <tt>YUM</tt> '
                   'for checking package update status.'),
)
