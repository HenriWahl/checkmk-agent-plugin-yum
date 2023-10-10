#!/usr/bin/env python3
#
# Check_MK YUM Plugin - Check for upgradeable packages.
#
# Copyright 2015, Henri Wahl <h.wahl@ifw-dresden.de>
# Copyright 2018, Moritz Schlarb <schlarbm@uni-mainz.de>
# Copyright 2021, Marco Lenhardt <marco.lenhardt@ontec.at>
# Copyright 2021, Henrik Gießel <henrik.giessel@yahoo.de>
# Copyright 2023, Timo Klecker <klecker@decoit.de>
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Example Agent Output:
#
# <<<yum>>>
# yes
# 32
# 4
# 1626252300

from time import time

from typing import Dict, List, NamedTuple, Optional

from cmk.gui.i18n import _
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    StringTable,
)
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    Result,
    Service,
    State,
    Metric,
    render,
)


class Section(NamedTuple):
    reboot_required: Optional[bool]
    packages: int = -1
    security_packages: int = -1
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
    last_update_timestamp = None
    try:
        packages = int(string_table[1][0])
        security_packages = int(string_table[2][0])
        last_update_timestamp = int(string_table[3][0])
    except KeyError:
        pass

    return Section(
        reboot_required,
        packages,
        security_packages,
        last_update_timestamp)


register.agent_section(
    name='yum',
    parse_function=yum_parse
)


def discovery_yum(section: Section):
    yield Service()


# the check function
def check_yum(params: Dict[str, int], section: Section):
    # Handle error message from agent
    if section.error_message:
        yield Result(state=State.UNKNOWN, summary=section.error_message)
        return

    if section.packages < 0:
        yield Result(state=State.UNKNOWN, summary='No package information available')
    elif section.packages == 0 and section.security_packages == 0:
        yield Result(state=State.OK, summary='All packages are up to date')
    elif section.packages > 0:
        yield Result(state=State(params.get("normal", 0)), summary=f"{section.packages} updates available")
        yield Metric(name="normal_updates", value=section.packages)

    if section.security_packages > 0:
        yield Result(state=State(params.get("security", 0)), summary=f"{section.security_packages} security updates available")
        yield Metric(name="security_updates", value=section.security_packages)

    if section.last_update_timestamp < 0:
        yield Result(
            state=State(params.get("last_update_state", 0)),
            summary=f"{section.last_update_timestamp} Time of last update could not be found")
        yield Metric(name="last_update_timestamp", value=section.last_update_timestamp)
    elif section.last_update_timestamp > 0:
        level = params.get("last_update_state", 0)
        last_update_time_diff = params.get("last_update_time_diff", (60*24*60*60))
        current_timestamp = int(time())

        if current_timestamp - section.last_update_timestamp < last_update_time_diff:
            yield Result(
                state=State.OK,
                summary=f"Last Update was run at {render.datetime(section.last_update_timestamp)}")
        elif current_timestamp - section.last_update_timestamp > last_update_time_diff and section.packages == 0:
            yield Result(
                state=State.OK,
                summary=f"Last Update was too long ago at {render.datetime(section.last_update_timestamp)} but there are no pending updates")
        else:
            yield Result(
                state=State(level),
                summary=f"Last Update was too long ago at {render.datetime(section.last_update_timestamp)} and there are pending updates")

    if section.reboot_required:
        # fallback for < 2.0.6
        if params is None:
            level = 2
        else:
            level = params["reboot_req"]
        yield Result(state=State(level),  summary="reboot required")


register.check_plugin(
    name='yum',
    service_name=_('YUM Updates'),
    discovery_function=discovery_yum,
    check_function=check_yum,
    sections=["yum"],
    check_ruleset_name="yum",
    check_default_parameters={
        "reboot_req": 2,
        "normal": 1,
        "security": 2,
        "last_update_state": 0,
        "last_update_time_diff": (60*24*60*60),
    },
)
