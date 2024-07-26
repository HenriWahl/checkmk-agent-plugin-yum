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

# Import the ability to set certain types of variable/object
from typing import Dict, List, NamedTuple, Optional

# Import CheckMK specific libraries
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

# Set some default values for the plugin
class Section(NamedTuple):
    reboot_required: Optional[bool]
    packages: int = -1
    security_packages: int = -1
    last_update_timestamp: int = -1
    error_message: Optional[str] = None

#### Define the section that processes the output received from the
#### agent within the 
# <<<yum>>> section. This is called because we register the "yum"
# agent section using the API "register" namespace
def yum_parse(string_table: List[List[str]]) -> Section:
    # If no results are determined to have been parsed from the agent
	# <<<yum>>> section, flag it
    if string_table[0][0] == 'ERROR:':
        return Section(error_message=" ".join(string_table[0][1:]))

    # Assess the validity of the "reboot_required" section - default to
	# "None" if there is an error
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

    # Return the processesed values if there has not been an error
    return Section(
        reboot_required,
        packages,
        security_packages,
        last_update_timestamp)

#### Register the agent section we want to be referring to
register.agent_section(
    # Using the apiv1 "register" namespace we register the "yum" agent
    # section and it's subsequent processing within this python script
    # by defining the "parse_funtcion" as "yum_parse"
    name='yum',
    parse_function=yum_parse
)

#### Define what we do when discovery is run
def discovery_yum(section: Section):
    yield Service()


#### Define the check function that is called by the registered
#### register.check_plugin section
def check_yum(params: Dict[str, int], section: Section):
    # Handle error message from agent which is set if the agent output
    # is not a correct format
    if section.error_message:
        yield Result(state=State.UNKNOWN, summary=section.error_message)
        return
    # Check the status returned from the agent script
    # Added additional checks to cover off a broader range of
    # possibilities and ensure that a value is returned (for
    # the perf-o-meter) even when no updates are available

    #### Check the status of "packages" (which is the "total updates
    #### available")
    # First check if there was an error returned (-1) where the yum
    # command failed
    if section.packages < 0:
        yield Result(state=State.UNKNOWN, summary='No package information available')
    # Then check if there are "no updates of which none are security
    # updates" but DO return a metric value of zero instead of not
    # having a metric value at all
    elif section.packages == 0 and section.security_packages == 0:
        yield Result(state=State.OK, summary='All packages are up to date')
        yield Metric(name="normal_updates", value=section.packages)
    # If there are "any" updates available report the number of updates
    elif section.packages > 0:
        yield Result(state=State(params.get("normal", 0)), summary=f"{section.packages} updates available")
        yield Metric(name="normal_updates", value=section.packages)
    # If there are no updates available, but we haven't been able to
    # check security updates, still return a metric value of zero
    elif section.packages == 0:
        yield Result(state=State.OK, summary=f"{section.packages} updates available")
        yield Metric(name="normal_updates", value=section.packages)

    # Check the status of the returned number of updates that are security updates including
	  # error condition and if there are no updates or the security updates check is not possible
    # First check if ANY updates were flagged as security updates and report the metric
    if section.security_packages > 0:
        yield Result(state=State(params.get("security", 0)), summary=f"{section.security_packages} security updates available")
        yield Metric(name="security_updates", value=section.security_packages)
    # If there are no updates available, report this
    elif section.security_packages == 0:
        yield Result(state=State.OK, summary=f"{section.security_packages} security updates available")
        yield Metric(name="security_updates", value=section.security_packages)
    # If the agent reported that security update was not available,
    # return this with a report of 0 updates
    elif section.security_packages == -2:
        yield Result(state=State.OK, summary='Security update check not available')
        yield Metric(name="security_updates", value=0)
    # If the security update check failed with an error,
    # report this AND a value of zero
    elif section.security_packages == -1:
        yield Metric(name="security_updates", value=0)
        yield Result(state=State.OK, summary='Security update failed')

        
    #### Interpret the timestamp that is returned for when the host was
    #### last updated
    # If the timestamp is less than zero, report that there is no
    # valid time stamp
    if section.last_update_timestamp < 0:
        yield Result(
            state=State(params.get("last_update_state", 0)),
            summary=f"{section.last_update_timestamp} Time of last update could not be found")
        yield Metric(name="last_update_timestamp", value=section.last_update_timestamp)
    # If not a value less than 0, assess the timestamp by first
    # grabbing all the relevant parameters
    elif section.last_update_timestamp > 0:
        # Get the default or WATO config state from within CheckMK api
        level = params.get("last_update_state", 0)
        # Get the threshold for the time we are allowed to be out by
        # from default or WATO
        last_update_time_diff = params.get("last_update_time_diff", (60*24*60*60))
        # Get current time so we can assess the age of OUR timestamp
        current_timestamp = int(time())
        # Delta the supplied timestamp and compare it to the target
        # from the default or WATO. If the last update delta is less
        # than the configured threshold, report OK
        if current_timestamp - section.last_update_timestamp < last_update_time_diff:
            yield Result(
                state=State.OK,
                summary=f"Last Update was run at {render.datetime(section.last_update_timestamp)}")
        # If the last update delta is outside of the configured
        # threshold but the number of configured packages is 0 then
        # still report all is OK, is there is nothing we could possibly
        # have updated
        elif current_timestamp - section.last_update_timestamp > last_update_time_diff and section.packages == 0:
            yield Result(
                state=State.OK,
                summary=f"Last Update was too long ago at {render.datetime(section.last_update_timestamp)} but there are no pending updates")
        # Otherwise, report the level that is configured in default or
        # WATO for being outside of the required delta time
        else:
            yield Result(
                state=State(level),
                summary=f"Last Update was too long ago at {render.datetime(section.last_update_timestamp)} and there are pending updates")
    
    #### Assess the "reboot_required" parameters
    if section.reboot_required:
        # fallback for < 2.0.6
        # If the reported value has been anything other than yes or no
        # then the value will be "None" as defined in the yum_parse
        # section if it is then report an error
        if params is None:
            level = 2
        else:
            level = params["reboot_req"]
        yield Result(state=State(level),  summary="reboot required")


#### Use the API v1 "register" namspace to assign the various
#### processing sections of this python file to handle that various
#### data,
# set default parameters and the general details of the service.
register.check_plugin(
    # Set the unique name of the plugin
    name='yum',
    # Set the service name that is created on a host 
    service_name=_('YUM Updates'),
    # Set what should be called when discovery is run - in this case,
    # call "discovery_yum" that simply creates a new service
    discovery_function=discovery_yum,
    # Set what the "check" function is - in this case, to check the
    # output from the agent once it has been processed by
    # "yum_parse" we will run "check_yum"
    check_function=check_yum,
    # Specify which agent section we need to read
    sections=["yum"],
    # specify which ruleset to grab parameters from
    check_ruleset_name="yum",
    # Set the default parameters (which match the ones defined in the
    # WATO ruleset in yum_check_parameters.py)
    check_default_parameters={
        "reboot_req": 2,
        "normal": 1,
        "security": 2,
        "last_update_state": 0,
        "last_update_time_diff": (60*24*60*60),
    },
)
