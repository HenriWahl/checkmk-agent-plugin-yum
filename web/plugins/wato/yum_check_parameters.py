#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# 2015 Henri Wahl <h.wahl@ifw-dresden.de>
# 2013 Karsten Schoeke karsten.schoeke@geobasis-bb.de

group = "checkparams"

subgroup_os =           _("Operating System Resources")

register_check_parameters(
    subgroup_os,
    "yum",
    _("YUM Update check"),
        None,
        None, None
)
