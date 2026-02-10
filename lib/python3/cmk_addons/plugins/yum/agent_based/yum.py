#!/usr/bin/env python3
"""Checkmk 2.4 agent-based check plugin for YUM/DNF package updates.

Monitors pending normal and security updates on RPM-based Linux distributions.
Supports Red Hat Enterprise Linux 8-10 and compatible derivatives.

Example agent output:

    <<<yum>>>
    yes
    32
    4 kernel,glibc,openssl
    1626252300
"""
#
# Copyright 2015, Henri Wahl <h.wahl@ifw-dresden.de>
# Copyright 2018, Moritz Schlarb <schlarbm@uni-mainz.de>
# Copyright 2021, Marco Lenhardt <marco.lenhardt@ontec.at>
# Copyright 2021, Henrik Giessel <henrik.giessel@yahoo.de>
# Copyright 2023, Timo Klecker <klecker@decoit.de>
#
# License: GPLv3+

from collections.abc import Mapping, Sequence
from time import time
from typing import NamedTuple

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    Metric,
    Result,
    Service,
    State,
    check_levels,
    render,
)


class YumSection(NamedTuple):
    """Parsed section data from the yum agent plugin."""

    reboot_required: bool | None = None
    packages: int = -1
    security_packages: int = -1
    security_packages_list: str | None = None
    last_update_timestamp: int = -1
    error_message: str | None = None


# ---------------------------------------------------------------------------
# Parse function
# ---------------------------------------------------------------------------


def parse_yum(string_table: Sequence[Sequence[str]]) -> YumSection:
    """Parse the ``<<<yum>>>`` agent section into a *YumSection*."""
    if not string_table:
        return YumSection(error_message="Empty agent output")

    if string_table[0][0] == "ERROR:":
        return YumSection(error_message=" ".join(string_table[0][1:]))

    reboot_required: bool | None = None
    if string_table[0][0] in ("yes", "no"):
        reboot_required = string_table[0][0] == "yes"

    packages = -1
    security_packages = -1
    security_packages_list: str | None = None
    last_update_timestamp = -1

    try:
        packages = int(string_table[1][0])
    except (IndexError, ValueError):
        pass

    try:
        security_packages = int(string_table[2][0])
        if len(string_table[2]) > 1:
            security_packages_list = string_table[2][1]
    except (IndexError, ValueError):
        pass

    try:
        last_update_timestamp = int(string_table[3][0])
    except (IndexError, ValueError):
        pass

    return YumSection(
        reboot_required=reboot_required,
        packages=packages,
        security_packages=security_packages,
        security_packages_list=security_packages_list,
        last_update_timestamp=last_update_timestamp,
    )


# ---------------------------------------------------------------------------
# Agent section registration
# ---------------------------------------------------------------------------

agent_section_yum = AgentSection(
    name="yum",
    parse_function=parse_yum,
)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def discover_yum(section: YumSection):
    """Discover one service if the yum section is present."""
    yield Service()


# ---------------------------------------------------------------------------
# Check function
# ---------------------------------------------------------------------------


def check_yum(params: Mapping[str, object], section: YumSection) -> CheckResult:
    """Evaluate available YUM/DNF updates against configurable thresholds."""
    if section.error_message:
        yield Result(state=State.UNKNOWN, summary=section.error_message)
        return

    if section.packages < 0:
        yield Result(state=State.UNKNOWN, summary="No package information available")
        return

    # --- Package updates -------------------------------------------------
    if section.packages == 0 and max(section.security_packages, 0) == 0:
        yield Result(state=State.OK, summary="All packages are up to date")
        yield Metric(name="normal_updates", value=0)
        yield Metric(name="security_updates", value=0)
    else:
        # Normal updates
        yield from check_levels(
            section.packages,
            levels_upper=params.get("normal", ("fixed", (1, 10))),
            metric_name="normal_updates",
            label="Normal updates",
            render_func=lambda v: str(int(v)),
        )

        # Security updates
        if section.security_packages >= 0:
            yield from check_levels(
                section.security_packages,
                levels_upper=params.get("security", ("fixed", (1, 1))),
                metric_name="security_updates",
                label="Security updates",
                render_func=lambda v: str(int(v)),
            )
            if section.security_packages_list and section.security_packages > 0:
                yield Result(
                    state=State.OK,
                    notice=f"Security packages: {section.security_packages_list}",
                )

    # Handle security-update edge states
    if section.security_packages == -2:
        yield Result(state=State.OK, notice="Security update check not available")
        yield Metric(name="security_updates", value=0)
    elif section.security_packages == -1:
        yield Result(state=State.OK, notice="Security update check failed")
        yield Metric(name="security_updates", value=0)

    # --- Last update timestamp -------------------------------------------
    if section.last_update_timestamp >= 0:
        threshold_days: int = int(params.get("last_update_time_diff", 60))
        threshold_seconds = threshold_days * 86400
        age = int(time()) - section.last_update_timestamp

        if age < threshold_seconds:
            yield Result(
                state=State.OK,
                summary=f"Last update: {render.datetime(section.last_update_timestamp)}",
            )
        elif section.packages == 0:
            yield Result(
                state=State.OK,
                notice=(
                    f"Last update was {render.datetime(section.last_update_timestamp)}"
                    ", but no updates available"
                ),
            )
        else:
            level = int(params.get("last_update_state", 1))
            yield Result(
                state=State(level),
                summary=f"Last update too long ago: {render.datetime(section.last_update_timestamp)}",
            )
    else:
        level = int(params.get("last_update_state", 1))
        yield Result(state=State(level), summary="No timestamp for last update available")

    # --- Reboot required -------------------------------------------------
    if section.reboot_required:
        level = int(params.get("reboot_req", 2))
        yield Result(state=State(level), summary="Reboot required")


# ---------------------------------------------------------------------------
# Check plugin registration
# ---------------------------------------------------------------------------

check_plugin_yum = CheckPlugin(
    name="yum",
    service_name="YUM Updates",
    discovery_function=discover_yum,
    check_function=check_yum,
    check_default_parameters={
        "normal": ("fixed", (1, 10)),
        "security": ("fixed", (1, 1)),
        "last_update_time_diff": 60,
        "last_update_state": 1,   # WARN
        "reboot_req": 2,          # CRIT
    },
    check_ruleset_name="yum",
)
