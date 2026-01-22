#!/usr/bin/env python3
#
# Check_MK YUM Plugin - Check for upgradeable packages.
#
# Copyright 2015, Henri Wahl <h.wahl@ifw-dresden.de>
# Copyright 2018, Moritz Schlarb <schlarbm@uni-mainz.de>
# Copyright 2021, Marco Lenhardt <marco.lenhardt@ontec.at>
# Copyright 2021, Henrik Gießel <henrik.giessel@yahoo.de>
# Copyright 2023, Timo Klecker <klecker@decoit.de>
#
# Based on:
#
# Check_MK APT-NG Plugin - Check for upgradeable packages.
#
# Copyright 2012, Stefan Schlesinger <sts@ono.at>
# Copyright 2015, Karsten Schoeke <karsten.schoeke@geobasis-bb.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>
#
#
# Example Agent Output:
#
# <<<yum>>>
# yes
# 32
# 4
# 1626252300

# Import the ability to manipulate and handle times in python

from time import time
from typing import Dict, List, NamedTuple, Optional
from cmk.gui.i18n import _
from cmk.agent_based.v2 import (
    CheckResult,
    CheckPlugin,
    Service,
    State,
    Metric,
    render,
    AgentSection,
    Result,
)


class Section(NamedTuple):
    reboot_required: Optional[bool]
    packages: int = -1
    security_packages: int = -1
    security_packages_list: Optional[str] = None
    last_update_timestamp: int = -1
    error_message: Optional[str] = None


def yum_parse(string_table: List[List[str]]) -> Section:
    if string_table[0][0] == 'ERROR:':
        return Section(error_message=" ".join(string_table[0][1:]))

    reboot_required = None
    try:
        if string_table[0][0] in ('yes', 'no'):
            reboot_required = string_table[0][0] == 'yes'
    except KeyError:
        pass

    packages = None
    security_packages = None
    security_packages_list = None
    last_update_timestamp = None
    try:
        packages = int(string_table[1][0])
        security_packages = int(string_table[2][0])
        if len(string_table[2]) > 1:
            security_packages_list = string_table[2][1]
        last_update_timestamp = int(string_table[3][0])
    except KeyError:
        pass

    return Section(
        reboot_required,
        packages,
        security_packages,
        security_packages_list,
        last_update_timestamp)


agent_section_yum = AgentSection(
    name="yum",
    parse_function=yum_parse,
)


def discovery_yum(section: Section):
    yield Service()


def check_yum(params: Dict[str, object], section: Section):
    debug = False

    if section.error_message:
        yield Result(state=State.UNKNOWN, summary=section.error_message)
        return

    if debug:
        details = ", ".join(f"{k}={v}" for k, v in params.items())
        yield Result(state=State.OK, summary="[DEBUG] YUM plugin running", details=details)

    # === Normal Updates ===
    if section.packages < 0:
        yield Result(state=State.UNKNOWN, summary="No package information available")
    elif section.packages == 0 and section.security_packages == 0:
        yield Result(state=State.OK, summary="All packages are up to date")
        yield Metric(name="normal_updates", value=0)
    else:
        mode, levels = params.get("normal")
        if mode == 'fixed':
            warn, crit = levels
            if section.packages >= crit:
                state = State.CRIT
            elif section.packages >= warn:
                state = State.WARN
            else:
                state = State.OK
        else:
            state = State.OK
        yield Result(state=state, summary=f"{section.packages} normal updates available")
        yield Metric(name="normal_updates", value=section.packages)

    # === Security Updates ===
    if section.security_packages >= 0:
        mode, levels = params.get("security")
        if mode == 'fixed':
            warn, crit = levels
            if section.security_packages >= crit:
                state = State.CRIT
            elif section.security_packages >= warn:
                state = State.WARN
            else:
                state = State.OK
        else:
            state = State.OK
        if section.security_packages_list:
            summary = f"{section.security_packages} security updates available ({section.security_packages_list})"
        else:
            summary = f"{section.security_packages} security updates available"
        yield Result(state=state, summary=summary)
        yield Metric(name="security_updates", value=section.security_packages)

    elif section.security_packages == -2:
        yield Result(state=State.OK, summary="Security update check not available")
        yield Metric(name="security_updates", value=0)

    elif section.security_packages == -1:
        yield Result(state=State.OK, summary="Security update check failed")
        yield Metric(name="security_updates", value=0)

    # === Last Update Timestamp ===
    if section.last_update_timestamp >= 0:
        threshold_days = params.get("last_update_time_diff", 60)
        threshold = threshold_days * 24 * 60 * 60
        level = params.get("last_update_state", State.WARN)
        age = int(time()) - section.last_update_timestamp

        if age < threshold:
            yield Result(
                state=State.OK,
                summary=f"Last update was at {render.datetime(section.last_update_timestamp)}",
            )
        elif section.packages == 0:
            yield Result(
                state=State.OK,
                summary=f"Last update was long ago at {render.datetime(section.last_update_timestamp)}, but no updates available",
            )
        else:
            yield Result(
                state=State(level),
                summary=f"Last update was too long ago at {render.datetime(section.last_update_timestamp)}",
            )
        yield Metric(name="last_update_timestamp", value=section.last_update_timestamp)
    else:
        level = params.get("last_update_state", State.WARN)
        yield Result(state=State(level), summary="No timestamp for last update available")
        yield Metric(name="last_update_timestamp", value=0)

    # === Reboot Required ===
    if section.reboot_required:
        level = params.get("reboot_req", State.CRIT)
        yield Result(state=State(level), summary="Reboot required")


check_plugin_yum = CheckPlugin(
    name='yum',
    service_name=_('YUM Updates'),
    discovery_function=discovery_yum,
    check_function=check_yum,
    sections=["yum"],
    check_ruleset_name="yum",
    check_default_parameters={
        "reboot_req": 2,
        "normal": ("fixed", (1, 10)),
        "security": ("fixed", (1, 1)),
        "last_update_state": 1,
        "last_update_time_diff": 60,
    },
)
