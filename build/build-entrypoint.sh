#!/usr/bin/env bash
# CLI steps done like described in https://docs.checkmk.com/latest/en/mkps.html

set -e

SOURCE=/source
CMK=/omd/sites/cmk

cd $CMK/local

# copy lib
cp -R $SOURCE/lib/* ./lib/

cd share/check_mk
# copy non-lib
cp -R $SOURCE/agents .
# No longer needed as all in lib
# cp -R $SOURCE/checkman .
# cp -R $SOURCE/web .

# needed for package config file creation
# has to be done by site user
su - cmk -c "/omd/sites/cmk/bin/mkp template yum"

# otherwise /source is not accepted
git config --global --add safe.directory $SOURCE

# modify extension config file with correct version number, author etc.
/build-modify-extension.py $SOURCE $CMK/tmp/check_mk/yum.manifest.temp

# avoid error:
# Error removing file /omd/sites/cmk/local/lib/python3/cmk/base/cee/plugins/bakery/yum.py: [Errno 13] Permission denied: '/omd/sites/cmk/local/lib/python3/cmk/base/cee/plugins/bakery/yum.py'
chmod go+rw $CMK/local/lib/python3/cmk/base/cee/plugins/bakery

# also to be done by site user is packaging the mkp file
su - cmk -c "/omd/sites/cmk/bin/mkp package $CMK/tmp/check_mk/yum.manifest.temp"

# copy created extension package back into volume
cp $CMK/var/check_mk/packages_local/*.mkp $SOURCE

# let runner user access the created mkp file which is owned by root now
chmod go+r $SOURCE/*.mkp
