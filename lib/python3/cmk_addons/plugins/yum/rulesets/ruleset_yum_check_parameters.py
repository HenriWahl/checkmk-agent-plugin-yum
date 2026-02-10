#!/usr/bin/env python3
"""Checkmk 2.4 ruleset for YUM/DNF update check parameters."""

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    LevelDirection,
    ServiceState,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition, Topic


def _parameter_form_yum() -> Dictionary:
    return Dictionary(
        title=Title("YUM/DNF Update Check"),
        help_text=Help(
            "Configure thresholds and states for the YUM/DNF update monitoring check."
        ),
        elements={
            "normal": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Levels for normal updates"),
                    help_text=Help(
                        "Set WARN/CRIT thresholds based on the number of pending normal updates."
                    ),
                    form_spec_template=Integer(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue(value=(1, 10)),
                ),
                required=False,
            ),
            "security": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Levels for security updates"),
                    help_text=Help(
                        "Set WARN/CRIT thresholds based on the number of pending security updates."
                    ),
                    form_spec_template=Integer(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue(value=(1, 1)),
                ),
                required=False,
            ),
            "reboot_req": DictElement(
                parameter_form=ServiceState(
                    title=Title("State when a reboot is required"),
                    prefill=DefaultValue(ServiceState.CRIT),
                ),
                required=False,
            ),
            "last_update_time_diff": DictElement(
                parameter_form=Integer(
                    title=Title("Maximum age of last update"),
                    help_text=Help(
                        "If no update has been applied within this many days "
                        "and updates are available, the service state changes."
                    ),
                    unit_symbol="days",
                    prefill=DefaultValue(60),
                ),
                required=False,
            ),
            "last_update_state": DictElement(
                parameter_form=ServiceState(
                    title=Title("State when last update is too old"),
                    prefill=DefaultValue(ServiceState.WARN),
                ),
                required=False,
            ),
        },
    )


rule_spec_yum = CheckParameters(
    name="yum",
    title=Title("YUM/DNF Update Check Parameters"),
    topic=Topic.OPERATING_SYSTEM,
    parameter_form=_parameter_form_yum,
    condition=HostCondition(),
)
