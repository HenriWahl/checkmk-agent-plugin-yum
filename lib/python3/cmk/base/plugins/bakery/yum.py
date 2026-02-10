#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bakery plugin for deploying the YUM/DNF update check agent plugin.

Uses Bakery API v1 — the current stable API for Checkmk 2.4.
"""
from pathlib import Path
from typing import Any

from .bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_yum_files(conf: Any) -> FileGenerator:
    """Yield the agent plugin file for deployment via the Agent Bakery."""
    deploy = conf.get("deploy")
    if deploy is None:
        return

    # Handle the cascading single-choice structure:
    #   ("interval", <float seconds>)  -> deploy with interval
    #   "nointerval"                    -> do not deploy
    if isinstance(deploy, str) and deploy == "nointerval":
        return
    if isinstance(deploy, tuple):
        choice, value = deploy
        if choice == "nointerval":
            return
        if choice == "interval" and value is not None:
            yield Plugin(
                base_os=OS.LINUX,
                source=Path("yum"),
                interval=int(value),
            )
            return

    # Fallback: deploy without caching interval
    yield Plugin(
        base_os=OS.LINUX,
        source=Path("yum"),
    )


register.bakery_plugin(
    name="yum",
    files_function=get_yum_files,
)
