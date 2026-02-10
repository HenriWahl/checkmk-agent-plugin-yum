#!/usr/bin/env python3
"""Unit tests for the YUM/DNF agent-based check plugin."""

import pytest
from collections.abc import Mapping
from typing import Any
from unittest.mock import patch

# Import the check plugin module
# When running inside Checkmk, these would be available; for standalone testing we mock them
try:
    from cmk_addons.plugins.yum.agent_based.yum import (
        YumSection,
        parse_yum,
        discover_yum,
        check_yum,
    )
except ImportError:
    # For standalone testing without Checkmk installed
    pytest.skip("Checkmk libraries not available", allow_module_level=True)


# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def default_params() -> Mapping[str, object]:
    """Default check parameters."""
    return {
        "normal": ("fixed", (1, 10)),
        "security": ("fixed", (1, 1)),
        "last_update_time_diff": 60,
        "last_update_state": 1,
        "reboot_req": 2,
    }


# =============================================================================
# Parse Function Tests
# =============================================================================


class TestParseYum:
    """Tests for the parse_yum function."""

    def test_parse_empty_output(self):
        """Empty agent output should return an error section."""
        result = parse_yum([])
        assert result.error_message == "Empty agent output"

    def test_parse_error_message(self):
        """Agent error messages should be captured."""
        result = parse_yum([["ERROR:", "MK_VARDIR", "not", "set"]])
        assert result.error_message == "MK_VARDIR not set"

    def test_parse_normal_output(self):
        """Standard agent output should be parsed correctly."""
        string_table = [
            ["no"],
            ["5"],
            ["2", "kernel,glibc"],
            ["1700000000"],
        ]
        result = parse_yum(string_table)

        assert result.reboot_required is False
        assert result.packages == 5
        assert result.security_packages == 2
        assert result.security_packages_list == "kernel,glibc"
        assert result.last_update_timestamp == 1700000000
        assert result.error_message is None

    def test_parse_reboot_required(self):
        """Reboot required flag should be detected."""
        string_table = [
            ["yes"],
            ["12"],
            ["1"],
            ["1700000000"],
        ]
        result = parse_yum(string_table)
        assert result.reboot_required is True

    def test_parse_security_unsupported(self):
        """Security updates unsupported (-2) should be handled."""
        string_table = [
            ["no"],
            ["3"],
            ["-2"],
            ["1700000000"],
        ]
        result = parse_yum(string_table)
        assert result.security_packages == -2

    def test_parse_security_failed(self):
        """Security check failure (-1) should be handled."""
        string_table = [
            ["no"],
            ["3"],
            ["-1"],
            ["1700000000"],
        ]
        result = parse_yum(string_table)
        assert result.security_packages == -1

    def test_parse_no_timestamp(self):
        """Missing timestamp (-1) should be handled."""
        string_table = [
            ["no"],
            ["0"],
            ["0"],
            ["-1"],
        ]
        result = parse_yum(string_table)
        assert result.last_update_timestamp == -1

    def test_parse_malformed_numbers(self):
        """Malformed numeric values should default gracefully."""
        string_table = [
            ["no"],
            ["not_a_number"],
            ["also_bad"],
            ["invalid"],
        ]
        result = parse_yum(string_table)
        assert result.packages == -1
        assert result.security_packages == -1
        assert result.last_update_timestamp == -1


# =============================================================================
# Discovery Tests
# =============================================================================


class TestDiscoverYum:
    """Tests for the discover_yum function."""

    def test_discover_creates_service(self):
        """Discovery should yield exactly one service."""
        section = YumSection()
        services = list(discover_yum(section))
        assert len(services) == 1


# =============================================================================
# Check Function Tests
# =============================================================================


class TestCheckYum:
    """Tests for the check_yum function."""

    def test_check_error_state(self, default_params):
        """Error messages should result in UNKNOWN state."""
        section = YumSection(error_message="Test error")
        results = list(check_yum(default_params, section))

        assert len(results) == 1
        assert results[0].state.value == 3  # UNKNOWN
        assert "Test error" in results[0].summary

    def test_check_no_packages_info(self, default_params):
        """Missing package info should result in UNKNOWN state."""
        section = YumSection(packages=-1)
        results = list(check_yum(default_params, section))

        assert any(r.state.value == 3 for r in results if hasattr(r, "state"))

    def test_check_all_up_to_date(self, default_params):
        """No pending updates should result in OK state."""
        section = YumSection(
            reboot_required=False,
            packages=0,
            security_packages=0,
            last_update_timestamp=2000000000,  # Recent
        )
        results = list(check_yum(default_params, section))

        # Should have OK summary for up-to-date
        summaries = [r.summary for r in results if hasattr(r, "summary")]
        assert any("up to date" in s for s in summaries)

    def test_check_normal_updates_warn(self, default_params):
        """Normal updates at warn threshold should result in WARN."""
        section = YumSection(
            reboot_required=False,
            packages=5,  # Above warn (1), below crit (10)
            security_packages=0,
            last_update_timestamp=2000000000,
        )
        results = list(check_yum(default_params, section))

        # Should have at least one WARN
        states = [r.state.value for r in results if hasattr(r, "state")]
        assert 1 in states  # WARN

    def test_check_normal_updates_crit(self, default_params):
        """Normal updates at crit threshold should result in CRIT."""
        section = YumSection(
            reboot_required=False,
            packages=15,  # Above crit (10)
            security_packages=0,
            last_update_timestamp=2000000000,
        )
        results = list(check_yum(default_params, section))

        states = [r.state.value for r in results if hasattr(r, "state")]
        assert 2 in states  # CRIT

    def test_check_security_updates_crit(self, default_params):
        """Security updates should trigger CRIT with default params."""
        section = YumSection(
            reboot_required=False,
            packages=1,
            security_packages=1,  # At crit threshold (1, 1)
            last_update_timestamp=2000000000,
        )
        results = list(check_yum(default_params, section))

        states = [r.state.value for r in results if hasattr(r, "state")]
        assert 2 in states  # CRIT

    def test_check_reboot_required(self, default_params):
        """Reboot required should trigger configured state."""
        section = YumSection(
            reboot_required=True,
            packages=0,
            security_packages=0,
            last_update_timestamp=2000000000,
        )
        results = list(check_yum(default_params, section))

        # Should have "Reboot required" result
        summaries = [r.summary for r in results if hasattr(r, "summary")]
        assert any("Reboot required" in s for s in summaries)

        # Should be CRIT (reboot_req=2)
        states = [r.state.value for r in results if hasattr(r, "state")]
        assert 2 in states

    def test_check_security_list_in_notice(self, default_params):
        """Security package list should appear in notice."""
        section = YumSection(
            reboot_required=False,
            packages=2,
            security_packages=2,
            security_packages_list="kernel,openssl",
            last_update_timestamp=2000000000,
        )
        results = list(check_yum(default_params, section))

        # Check for notice with package list
        notices = [r.notice for r in results if hasattr(r, "notice") and r.notice]
        assert any("kernel,openssl" in n for n in notices)


# =============================================================================
# Integration-style Tests (with mocked time)
# =============================================================================


class TestCheckYumWithMockedTime:
    """Tests that require mocking time.time()."""

    @patch("cmk_addons.plugins.yum.agent_based.yum.time")
    def test_check_last_update_recent(self, mock_time, default_params):
        """Recent last update should be OK."""
        mock_time.return_value = 1700100000  # ~1 day after last update

        section = YumSection(
            reboot_required=False,
            packages=0,
            security_packages=0,
            last_update_timestamp=1700000000,
        )
        results = list(check_yum(default_params, section))

        # Should not have warning about last update
        assert not any(
            "too long ago" in getattr(r, "summary", "")
            for r in results
            if hasattr(r, "summary")
        )

    @patch("cmk_addons.plugins.yum.agent_based.yum.time")
    def test_check_last_update_old(self, mock_time, default_params):
        """Old last update with pending updates should warn."""
        mock_time.return_value = 1710000000  # ~115 days after last update

        section = YumSection(
            reboot_required=False,
            packages=5,  # Updates available
            security_packages=0,
            last_update_timestamp=1700000000,
        )
        results = list(check_yum(default_params, section))

        summaries = [r.summary for r in results if hasattr(r, "summary")]
        assert any("too long ago" in s for s in summaries)
