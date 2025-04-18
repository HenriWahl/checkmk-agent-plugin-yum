#!/usr/bin/env python3
#
#  modify extension configuration

# Include "os" to check for correct copy of the yum agent before changing lines in it below
import os

from pathlib import Path
from pprint import pformat
from sys import argv, \
    exit

from git import (Commit,
                 Repo,
                 TagReference)
version="0.0.0"
# only do stuff if git repo path and config file path are given
if len(argv) > 2:
    git_repo_path = argv[1]
    package_file_path = argv[2]
    if Path(package_file_path).exists() and Path(package_file_path).is_file():
        # get version information from git repo
        repo = Repo(path=git_repo_path, search_parent_directories=True)

        print(repo.head.commit)

        # if no tag is latest take repo head
        version_repo = next((tag for tag in repo.tags if tag.commit == repo.head.commit), repo.head.commit)
        if type(version_repo) == Commit:
            # first 8 characters of commit added to '0.0.' to get a SemVer version number
            version = f'0.0.{int(version_repo.hexsha[0:8], 16)}'
        elif type(version_repo) == TagReference:
            # Tag
            version = version_repo.name
            if version.startswith('v'):
                version = version.split('v')[1]

        # open package config file
        with open(package_file_path, 'r') as package_file:
            package_config = eval(package_file.read())

        # modify package config
        package_config['author'] = 'Henri Wahl'
        package_config['description'] = 'Checks for updates on RPM-based distributions via yum.'
        package_config['download_url'] = 'https://github.com/HenriWahl/checkmk-agent-plugin-yum/releases'
        package_config['title'] = 'YUM Update Check'
        package_config['version'] = version
        package_config['version.min_required'] = '2.0.0'

        # write package config file
        bla = pformat(package_config, indent=4)
        with open(package_file_path, 'w') as package_file:
            # nicely format config file with pformat
            package_file.write(pformat(package_config, indent=4))
    else:
        print(f'Package configuration file path {package_file_path} does not exist. :-(')
        exit(1)

    # New code to update version number inside the yum script itself
    yum_agent_path = "/omd/sites/cmk/local/share/check_mk/agents/plugins/yum"
    if os.path.exists(yum_agent_path):
        with open(yum_agent_path, "r+") as file:
            content = file.read().replace('CMK_VERSION="0.0.0"', f'CMK_VERSION="{version}"')
            file.seek(0)
            file.write(content)
            file.truncate()
    else:
        print(f"File not found: {yum_agent_path}")
    # End of new code

else:
    print('Git repository or package configuration file path is missing at all. :-(')
    exit(1)
