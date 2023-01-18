#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

try:
    from cmk.gui.i18n import _
    from cmk.gui.plugins.wato import (
        HostRulespec,
        rulespec_registry,
    )
    from cmk.gui.cee.plugins.wato.agent_bakery.rulespecs.utils import RulespecGroupMonitoringAgentsAgentPlugins
    from cmk.gui.valuespec import (
        Alternative,
        Age,
        Dictionary,
        FixedValue,
    )

    def _valuespec_agent_config_yum():
        return Alternative(
            title = _("Yum (Community Version) updates (Linux)"),
            help = _("This will deploy the agent plugin <tt>yum</tt>. This will activate the "
                     "check <tt>zypper</tt> on redHat based hosts and monitor pending normal and security updates."),
            elements = [
                Dictionary(
                    title = _("Deploy the Yum plugin"),
                    elements = [
                        ( "interval",
                          Age(title = "Interval for checking for updates"),
                        ),
                    ],
                    optional_keys = False,
                ),
                FixedValue(None, title = _("Do not deploy the Yum plugin"), totext = _("(disabled)")),
            ],
            default_value = { "interval": 129600, },
        )

    rulespec_registry.register(
        HostRulespec(
            group=RulespecGroupMonitoringAgentsAgentPlugins,
            name="agent_config:yum",
            valuespec=_valuespec_agent_config_yum,
        ))

except ModuleNotFoundError:
    # RAW edition
    pass
