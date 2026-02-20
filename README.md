# Checkmk Agent Plugin — YUM / DNF Update Check

A [Checkmk](https://checkmk.com) extension package (MKP) that monitors
available package updates on RPM-based Linux distributions.

> **Checkmk ≥ 2.4.0** is required.
> This plugin uses the **Agent Based API v2**, **Rulesets API v1**,
> **Bakery API v1**, and **Graphing API v1**.

Forked from <https://github.com/HenriWahl/checkmk-agent-plugin-yum> and
modernised for the Checkmk 2.4 plugin APIs.

---

## Supported Distributions

| Distribution | Versions | Package Manager |
|---|---|---|
| Red Hat Enterprise Linux (RHEL) | 8, 9, 10 | dnf / dnf5 |
| AlmaLinux | 8, 9, 10 | dnf / dnf5 |
| Rocky Linux | 8, 9, 10 | dnf / dnf5 |
| Oracle Linux | 8, 9, 10 | dnf / dnf5 |
| CentOS Stream | 8, 9, 10 | dnf / dnf5 |

The agent plugin automatically detects the best available package manager
(`dnf5` → `dnf` → `yum`).

---

## Features

- **Update count** — reports the total number of available package updates.
- **Security update count** — reports security-classified updates separately
  (with an optional package list in the service details).
- **Reboot detection** — compares the running kernel against the latest
  installed kernel to flag pending reboots.
- **Last update age** — warns when the system has not been updated within a
  configurable number of days.
- **Cache-aware** — re-uses cached results until the local package-manager
  cache changes, avoiding expensive `dnf` calls on every agent run.
- **WATO rules** — fully configurable thresholds via the Checkmk GUI.
- **Agent Bakery** — deploy the agent plugin automatically, with an optional
  async execution interval.
- **Graphing** — metrics for normal and security update counts with a
  combined graph definition.

---

## Installation

### From a release MKP

1. Download the latest `.mkp` file from the
   [Releases](https://github.com/HenriWahl/checkmk-agent-plugin-yum/releases)
   page.
2. Upload and install via **Setup → Maintenance → Extension packages** in the
   Checkmk GUI, or with the CLI:

   ```bash
   mkp install yum-<version>.mkp
   ```

### Manual (development)

Copy the file tree under `lib/` into
`~/local/lib/` of your Checkmk site and the `agents/` tree into
`~/local/share/check_mk/agents/`.

---

## Configuration

### Check Parameters

**Setup → Services → Service monitoring rules → YUM Updates**

| Parameter | Description | Default |
|---|---|---|
| Normal updates | WARN / CRIT thresholds on the number of pending updates | 1 / 10 |
| Security updates | WARN / CRIT thresholds on the number of security updates | 1 / 1 |
| Reboot required | Service state when a reboot is pending | CRIT |
| Last update age | Days after which missing updates trigger an alert | 60 |
| Last update state | Service state for the "too old" condition | WARN |

### Agent Bakery

**Setup → Agents → Windows, Linux, Solaris, AIX → Agent rules → YUM Update Check (Linux)**

Deploy the agent plugin to hosts via the Agent Bakery.
Optionally configure an asynchronous execution interval (in seconds) so the
plugin runs in the background at a fixed cadence rather than on every agent
call.

---

## File Layout

```
agents/
  plugins/
    yum                          # Bash agent plugin (deployed to monitored hosts)
lib/python3/
  cmk/base/plugins/bakery/
    yum.py                       # Bakery plugin (Agent Bakery deployment)
  cmk_addons/plugins/yum/
    agent_based/
      yum.py                     # Server-side check plugin (Agent Based API v2)
    checkman/
      yum                        # Checkmk manual page
    graphing/
      graphing_yum.py            # Metric & graph definitions (Graphing API v1)
    rulesets/
      ruleset_yum_bakery.py      # WATO ruleset: bakery configuration
      ruleset_yum_check_parameters.py  # WATO ruleset: check thresholds
build/
  Containerfile                  # Container build environment (CMK 2.4 Raw)
  build-entrypoint.sh            # Packages the MKP inside the container
  build-modify-extension.py      # Injects git version into the manifest
tests/
  test_check_yum.py              # Python unit tests (pytest)
  test_agent_yum.bats            # Shell tests (BATS)
```

---

## Building from Source

The build runs inside a Checkmk container to ensure the correct `mkp`
tooling is available. Both **Docker** and **Podman** are supported.

### Using Podman (recommended)

```bash
# Build the container image
podman build --format docker -t checkmk-yum-build -f build/Containerfile .

# Run the build (produces an MKP in the repo root)
podman run --rm -v "$PWD:/source:Z" checkmk-yum-build
```

> **Note:** The `:Z` suffix is required on SELinux-enabled systems (RHEL,
> Fedora) to relabel the volume for container access. The `--format docker`
> flag suppresses HEALTHCHECK warnings from the base image.

### Using Docker

```bash
docker build -t checkmk-yum-build -f build/Containerfile .
docker run --rm -v "$PWD:/source" checkmk-yum-build
```

### Build Output

The resulting `yum-<version>.mkp` file is written to the repository root.

A version number is derived automatically:

- If the current commit is tagged (e.g. `v1.2.3`), the tag is used.
- Otherwise a numeric version is generated from the commit hash.

---

## Development

### Prerequisites

Install development tools:

```bash
# RHEL/Fedora
dnf install bats ShellCheck python3-pip
pip install ruff mypy pytest

# Debian/Ubuntu
apt install bats shellcheck python3-pip
pip install ruff mypy pytest
```

### Makefile Targets

A Makefile is provided for convenience:

```bash
make lint         # Run all linters (shellcheck, ruff)
make format       # Auto-format Python code
make typecheck    # Run mypy type checker
make test         # Run all tests
make build        # Build the MKP package
make clean        # Remove build artifacts
```

### Linting

```bash
# Shell linting
shellcheck agents/plugins/yum

# Python linting
ruff check lib/ build/build-modify-extension.py

# Python formatting (check)
ruff format --check lib/

# Type checking
mypy --ignore-missing-imports build/build-modify-extension.py
```

### Testing

**Shell Tests (BATS):**

```bash
bats tests/test_agent_yum.bats
```

**Python Unit Tests:**

Requires access to Checkmk libraries (run inside a Checkmk site):

```bash
pytest tests/
```

---

## Upstream

This is a fork of the original plugin by Henri Wahl:

- **Upstream repository:** <https://github.com/HenriWahl/checkmk-agent-plugin-yum>

To pull updates from upstream:

```bash
git fetch upstream
git merge upstream/main  # or upstream/master
```

---

## License

[GPL-2.0](LICENSE)
