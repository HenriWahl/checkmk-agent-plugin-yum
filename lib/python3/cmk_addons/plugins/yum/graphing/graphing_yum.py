#!/usr/bin/env python3
"""Checkmk 2.4 graphing definitions for the YUM/DNF update check."""

from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.metrics import Color, DecimalNotation, Metric, Unit

# ---------------------------------------------------------------------------
# Metric definitions
# ---------------------------------------------------------------------------

metric_yum_normal_updates = Metric(
    name="normal_updates",
    title=Title("Normal updates available"),
    unit=Unit(DecimalNotation("")),
    color=Color.YELLOW,
)

metric_yum_security_updates = Metric(
    name="security_updates",
    title=Title("Security updates available"),
    unit=Unit(DecimalNotation("")),
    color=Color.RED,
)

# ---------------------------------------------------------------------------
# Graph definitions
# ---------------------------------------------------------------------------

graph_yum_updates = Graph(
    name="yum_updates",
    title=Title("Available package updates"),
    simple_lines=["normal_updates", "security_updates"],
    minimal_range=MinimalRange(0, 10),
)
