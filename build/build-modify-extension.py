#!/usr/bin/env python3
"""Modify the MKP extension manifest with version and metadata."""

import ast
import sys
from pathlib import Path
from pprint import pformat

from git import Commit, Repo, TagReference

CMK_AGENT_PATH = Path("/omd/sites/cmk/local/share/check_mk/agents/plugins/yum")

PACKAGE_METADATA = {
    "author": "Henri Wahl",
    "description": (
        "Checks for available package updates on RPM-based distributions "
        "(RHEL 8-10, AlmaLinux, Rocky Linux, Oracle Linux, CentOS Stream) "
        "via dnf5, dnf, or yum."
    ),
    "download_url": "https://github.com/HenriWahl/checkmk-agent-plugin-yum/releases",
    "title": "YUM/DNF Update Check",
    "version.min_required": "2.4.0",
}


def get_version_from_git(repo_path: str) -> str:
    """Derive a SemVer version string from the git repository state."""
    repo = Repo(path=repo_path, search_parent_directories=True)
    print(f"HEAD commit: {repo.head.commit}")

    version_ref = next(
        (tag for tag in repo.tags if tag.commit == repo.head.commit),
        repo.head.commit,
    )

    if isinstance(version_ref, Commit):
        # No tag on HEAD — use first 8 hex chars of the commit hash.
        return f"0.0.{int(version_ref.hexsha[:8], 16)}"

    if isinstance(version_ref, TagReference):
        tag_name = version_ref.name
        return tag_name.removeprefix("v")

    return "0.0.0"


def update_manifest(manifest_path: Path, version: str) -> None:
    """Read the MKP manifest, inject metadata, and write it back."""
    # ast.literal_eval is safe — it only evaluates literal expressions.
    package_config = ast.literal_eval(manifest_path.read_text())

    package_config.update(PACKAGE_METADATA)
    package_config["version"] = version

    manifest_path.write_text(pformat(package_config, indent=4) + "\n")
    print(f"Manifest updated: version={version}")


def stamp_agent_version(version: str) -> None:
    """Replace the placeholder version in the deployed agent plugin."""
    if not CMK_AGENT_PATH.exists():
        print(f"WARNING: Agent plugin not found at {CMK_AGENT_PATH}")
        return

    content = CMK_AGENT_PATH.read_text()
    CMK_AGENT_PATH.write_text(
        content.replace('CMK_VERSION="0.0.0"', f'CMK_VERSION="{version}"')
    )
    print(f"Agent plugin stamped with version {version}")


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: build-modify-extension.py <git-repo-path> <manifest-path>")
        sys.exit(1)

    git_repo_path = sys.argv[1]
    manifest_path = Path(sys.argv[2])

    if not manifest_path.is_file():
        print(f"ERROR: Manifest file not found: {manifest_path}")
        sys.exit(1)

    version = get_version_from_git(git_repo_path)
    update_manifest(manifest_path, version)
    stamp_agent_version(version)


if __name__ == "__main__":
    main()
