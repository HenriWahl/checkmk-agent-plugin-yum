#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

group = "agents/" + _("Agent Plugins")

register_rule(group,
    "agent_config:yum",
    Alternative(
        title = _("YUM (Community Version) updates (Linux)"),
        help = _("This will deploy the agent plugin <tt>yum</tt>. This will activate the "
                 "check <tt>yum</tt> on RedHat based hosts and monitor pending normal and security updates."),
        style = "dropdown",
        elements = [
            Dictionary(
                title = _("Deploy the YUM plugin"),
                elements = [
                    ( "interval",
                      Age(title = "Interval for checking updates"),
                    ),
                ],
                optional_keys = False,
            ),
            FixedValue(None, title = _("Do not deploy the YUM plugin"), totext = _("(disabled)")),
        ],
        default_value = { "interval": 129600, },
    )
)
