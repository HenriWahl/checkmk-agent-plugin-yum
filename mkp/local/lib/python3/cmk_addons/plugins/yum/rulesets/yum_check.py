#!/usr/bin/env python3
"""Checkmk 2.4 rule specification for YUM Update Check"""

from cmk.rulesets.v1 import Help, Label, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    LevelDirection,
    SimpleLevels,
    ServiceState,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostCondition


def _parameter_form_yum():
    return Dictionary(
        title=Title("YUM Update Check"),
        elements={
            "reboot_req": DictElement(
                parameter_form=ServiceState(
                    title=Title("State when a reboot is required"),
                    prefill=DefaultValue(ServiceState.CRIT),
                ),
                required=False,
            ),
            "normal": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("State when normal updates are available"),
                    form_spec_template=Integer(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue(value=(1, 10)),
                ),
                required=False,
            ),
            "security": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("State when security updates are available"),
                    form_spec_template=Integer(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue(value=(1, 1)),
                ),
                required=False,
            ),
            "last_update_time_diff": DictElement(
                parameter_form=Integer(
                    title=Title("Max Time since last run update (Default 60 days)"),
                    unit_symbol="days",
                    prefill=DefaultValue(60),
                ),
                required=False
            ),
            "last_update_state": DictElement(
                parameter_form=ServiceState(
                    title=Title("Change State based on last run update (default OK)"),
                    prefill=DefaultValue(ServiceState.OK),
                ),
                required=False,
            ),
            "last_update_ignore": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Ignore time of last update"),
                    label=Label("Only show the time of the last update, do not change the state"),
                    help_text=Help(
                        "Useful if updates are installed by other tools like Ansible. When enabled, "
                        "the time of the last update is only shown in the service output and "
                        "neither its age nor a missing timestamp affects the service state."
                    ),
                    prefill=DefaultValue(False),
                ),
                required=False,
            ),
        }
    )


rule_spec_yum = CheckParameters(
    name="yum",
    title=Title("YUM Update Check Parameters"),
    topic=Topic.OPERATING_SYSTEM,
    parameter_form=_parameter_form_yum,
    condition=HostCondition(),
)
