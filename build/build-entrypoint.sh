#!/usr/bin/env bash
# Build entrypoint: packages the YUM/DNF check plugin as an MKP extension.
# Runs inside the Checkmk Docker container.
# See https://docs.checkmk.com/latest/en/mkps.html

set -e

SOURCE=/source
CMK=/omd/sites/cmk

cd "$CMK/local"

# Copy plugin library files into the site's local hierarchy
cp -R "$SOURCE/lib/"* ./lib/

cd share/check_mk
# Copy agent plugin
cp -R "$SOURCE/agents" .

# Create the MKP manifest template (must be run as site user)
su - cmk -c "/omd/sites/cmk/bin/mkp template yum"

# Allow git operations on the mounted source directory
git config --global --add safe.directory "$SOURCE"

# Inject version number and metadata into the manifest
/build-modify-extension.py "$SOURCE" "$CMK/tmp/check_mk/yum.manifest.temp"

# Ensure the site user can write to plugin directories during packaging
chmod go+rw "$CMK/local/lib/python3/cmk/base/plugins/bakery"
chmod go+rw "$CMK/local/lib/python3/cmk_addons/plugins/yum/agent_based"
chmod go+rw "$CMK/local/lib/python3/cmk_addons/plugins/yum/checkman"
chmod go+rw "$CMK/local/lib/python3/cmk_addons/plugins/yum/graphing"
chmod go+rw "$CMK/local/lib/python3/cmk_addons/plugins/yum/rulesets"

# Package the MKP (must be run as site user)
su - cmk -c "/omd/sites/cmk/bin/mkp package $CMK/tmp/check_mk/yum.manifest.temp"

# Copy the built MKP back to the mounted source volume
cp "$CMK/var/check_mk/packages_local/"*.mkp "$SOURCE"

# Let the CI runner user read the created MKP file
chmod go+r "$SOURCE/"*.mkp
