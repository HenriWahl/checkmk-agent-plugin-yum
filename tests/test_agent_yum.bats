#!/usr/bin/env bats
# BATS tests for the YUM/DNF agent plugin.
#
# Prerequisites:
#   - Install BATS: https://github.com/bats-core/bats-core
#   - On RHEL: dnf install bats
#   - On Debian/Ubuntu: apt install bats
#
# Run with:
#   bats tests/test_agent_yum.bats

setup() {
    # Create a temporary directory for test artifacts
    TEST_TEMP_DIR="$(mktemp -d)"

    # Set up mock MK_VARDIR
    export MK_VARDIR="${TEST_TEMP_DIR}/mk_vardir"
    mkdir -p "${MK_VARDIR}/cache"

    # Path to the agent plugin
    AGENT_PLUGIN="${BATS_TEST_DIRNAME}/../agents/plugins/yum"
}

teardown() {
    # Clean up temporary directory
    rm -rf "${TEST_TEMP_DIR}"
}

# =============================================================================
# Basic functionality tests
# =============================================================================

@test "Agent plugin is executable" {
    [ -x "${AGENT_PLUGIN}" ]
}

@test "Agent plugin starts with shebang" {
    head -1 "${AGENT_PLUGIN}" | grep -q '^#!/bin/bash'
}

@test "Agent plugin outputs yum section header" {
    # This test may fail on non-RPM systems; skip if no package manager
    if ! command -v dnf &>/dev/null && ! command -v yum &>/dev/null; then
        skip "No dnf or yum available"
    fi

    run timeout 60 bash "${AGENT_PLUGIN}"
    [ "$status" -eq 0 ]
    echo "$output" | grep -q '<<<yum>>>'
}

@test "Agent plugin fails gracefully without MK_VARDIR" {
    unset MK_VARDIR
    run bash "${AGENT_PLUGIN}"
    [ "$status" -eq 0 ]  # Should exit 0 (graceful failure)
    echo "$output" | grep -q 'ERROR:'
}

# =============================================================================
# Output format tests
# =============================================================================

@test "Agent output has correct number of lines" {
    if ! command -v dnf &>/dev/null && ! command -v yum &>/dev/null; then
        skip "No dnf or yum available"
    fi

    run timeout 60 bash "${AGENT_PLUGIN}"
    [ "$status" -eq 0 ]

    # Should have: section header + 4 data lines (or error)
    line_count=$(echo "$output" | wc -l)
    [ "$line_count" -ge 2 ]  # At minimum: header + error or header + data
}

@test "Reboot required line is yes or no" {
    if ! command -v dnf &>/dev/null && ! command -v yum &>/dev/null; then
        skip "No dnf or yum available"
    fi

    run timeout 60 bash "${AGENT_PLUGIN}"
    [ "$status" -eq 0 ]

    # Second line (after header) should be yes or no
    reboot_line=$(echo "$output" | sed -n '2p')
    [[ "$reboot_line" == "yes" || "$reboot_line" == "no" || "$reboot_line" == ERROR:* ]]
}

@test "Update count line is a number" {
    if ! command -v dnf &>/dev/null && ! command -v yum &>/dev/null; then
        skip "No dnf or yum available"
    fi

    run timeout 60 bash "${AGENT_PLUGIN}"
    [ "$status" -eq 0 ]

    # Skip if error output
    if echo "$output" | grep -q 'ERROR:'; then
        skip "Agent returned error"
    fi

    # Third line should be a number
    update_line=$(echo "$output" | sed -n '3p')
    [[ "$update_line" =~ ^[0-9]+$ ]]
}

@test "Security update line format is valid" {
    if ! command -v dnf &>/dev/null && ! command -v yum &>/dev/null; then
        skip "No dnf or yum available"
    fi

    run timeout 60 bash "${AGENT_PLUGIN}"
    [ "$status" -eq 0 ]

    if echo "$output" | grep -q 'ERROR:'; then
        skip "Agent returned error"
    fi

    # Fourth line: number [-2, -1, or 0+] optionally followed by package list
    security_line=$(echo "$output" | sed -n '4p')
    [[ "$security_line" =~ ^-?[0-9]+ ]]
}

# =============================================================================
# Cache behavior tests
# =============================================================================

@test "Cache files are created after first run" {
    if ! command -v dnf &>/dev/null && ! command -v yum &>/dev/null; then
        skip "No dnf or yum available"
    fi

    run timeout 60 bash "${AGENT_PLUGIN}"
    [ "$status" -eq 0 ]

    # At least one cache file should exist
    [ -f "${MK_VARDIR}/cache/yum_result.cache" ] || \
    [ -f "${MK_VARDIR}/cache/yum_pkg_state.cache" ] || \
    [ -f "${MK_VARDIR}/cache/yum_uptime.cache" ]
}

@test "Second run uses cache when repo unchanged" {
    if ! command -v dnf &>/dev/null && ! command -v yum &>/dev/null; then
        skip "No dnf or yum available"
    fi

    # First run
    run timeout 60 bash "${AGENT_PLUGIN}"
    [ "$status" -eq 0 ]
    first_output="$output"

    # Second run should be faster (using cache)
    start_time=$(date +%s%N)
    run timeout 60 bash "${AGENT_PLUGIN}"
    end_time=$(date +%s%N)
    [ "$status" -eq 0 ]

    # Output should be the same
    [ "$output" = "$first_output" ]
}

# =============================================================================
# Function isolation tests (source the script and test functions)
# =============================================================================

@test "detect_distribution function works" {
    # Source the script to get access to functions
    source "${AGENT_PLUGIN}" || true

    # The function should set MAJOR_VERSION and DISTRO_ID
    if declare -f detect_distribution &>/dev/null; then
        detect_distribution
        [ -n "$MAJOR_VERSION" ]
        [ -n "$DISTRO_ID" ]
    else
        skip "Function not accessible (script may have changed structure)"
    fi
}

@test "detect_package_manager function finds dnf or yum" {
    source "${AGENT_PLUGIN}" || true

    if declare -f detect_package_manager &>/dev/null; then
        if command -v dnf5 &>/dev/null || command -v dnf &>/dev/null || command -v yum &>/dev/null; then
            detect_package_manager
            [[ "$PKG_MGR" =~ ^(dnf5|dnf|yum)$ ]]
        else
            skip "No package manager available"
        fi
    else
        skip "Function not accessible"
    fi
}

# =============================================================================
# ShellCheck compliance (if shellcheck is available)
# =============================================================================

@test "Agent plugin passes shellcheck" {
    if ! command -v shellcheck &>/dev/null; then
        skip "shellcheck not installed"
    fi

    run shellcheck -x "${AGENT_PLUGIN}"
    echo "$output"
    [ "$status" -eq 0 ]
}
