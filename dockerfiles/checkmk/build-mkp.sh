#!/usr/bin/env bash
set -euo pipefail

CMK="/omd/sites/cmk"
SU="su - cmk -c"
WORKDIR="${PWD:-$(pwd)}"

# Copy local extension sources into the Check_MK local directory
cp -r mkp/local/* "${CMK}/local"

# Create temporary directory as the cmk user
$SU "mkdir -p ${CMK}/tmp/check_mk"

# Create mkp template (runs as cmk user)
$SU "mkp template yum"

# Mark repo safe for git (needed when running as different user)
git config --global --add safe.directory "${WORKDIR}"

# Run the extension modifier script to produce a manifest template
modify-extension.py "${WORKDIR}" "${CMK}/tmp/check_mk/yum.manifest.temp"

# Fix permissions to avoid Permission denied during mkp package
chmod go+rw "${CMK}/local/lib/python3/cmk/base/cee/plugins/bakery"
chmod go+rw "${CMK}/local/lib/python3/cmk_addons/plugins/yum/agent_based"
chmod go+rw "${CMK}/local/lib/python3/cmk_addons/plugins/yum/checkman"
chmod go+rw "${CMK}/local/lib/python3/cmk_addons/plugins/yum/rulesets"

# Show generated manifest and build the mkp package (runs as cmk user)
cat "${CMK}/tmp/check_mk/yum.manifest.temp"
$SU "mkp package ${CMK}/tmp/check_mk/yum.manifest.temp"

# Copy created mkp back to the workspace
mkdir -p "${WORKDIR}/mkp"
cp "${CMK}/var/check_mk/packages_local/"*.mkp "${WORKDIR}/mkp/"