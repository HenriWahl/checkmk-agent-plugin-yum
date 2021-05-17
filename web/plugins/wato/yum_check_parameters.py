#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# 2018 Moritz Schlarb <schlarbm@uni-mainz.de>
# 2015 Henri Wahl <h.wahl@ifw-dresden.de>
# 2013 Karsten Schoeke karsten.schoeke@geobasis-bb.de

group = "checkparams"

subgroup_os =           _("Operating System Resources")

register_check_parameters(
    subgroup_os,
    "yum",
    _("YUM Update check"),
    Dictionary(
        elements = [
            ("reboot_req",
                MonitoringState(
                    title = _("State when a reboot is required"),
                    default_value = 2,
            )),
            ("normal",
                MonitoringState(
                    title = _("State when normal updates are available"),
                    default_value = 1,
            )),
            ("security",
                MonitoringState(
                    title = _("State when security updates are available"),
                    default_value = 2,
            )),
        ]
    ),
    None,
    match_type = "dict",
)
