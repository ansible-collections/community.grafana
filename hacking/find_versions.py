#!/usr/bin/env python

import json
import requests
import re
import sys


class GitHubReleases:
    def __init__(self, repo):
        self.github_api = "https://api.github.com"
        self.repo = repo

    def fetch_releases(self):
        r = requests.get(
            f"{self.github_api}/repos/{self.repo}/releases?per_page=100",
            headers={"Accept": "application/vnd.github.v3+json"},
        )
        if r.status_code != 200:
            raise Exception(
                f"Failed to fetch releases for {self.repo}: {r.status_code}"
            )
        return r.json()


class AnsibleReleases(GitHubReleases):
    def normalize_version(self, version):
        if version.startswith("v"):
            version = version[1:]
        parts = re.split(r"[.-]", version)
        normalized = []
        for part in parts[:3]:
            number = "".join(filter(str.isdigit, part))
            normalized.append(int(number) if number else 0)
        return tuple(normalized)

    def get_latest_versions(self):
        releases = self.fetch_releases()
        stable_releases = {}

        for release in releases:
            tag_name = release.get("tag_name", "")
            if not tag_name.startswith("v"):
                continue

            if release.get("prerelease") or any(
                x in tag_name for x in ["alpha", "beta", "rc", "b"]
            ):
                continue

            version_tuple = self.normalize_version(tag_name)
            major_minor = (version_tuple[0], version_tuple[1])
            if (
                major_minor not in stable_releases
                or stable_releases[major_minor] < version_tuple
            ):
                stable_releases[major_minor] = version_tuple

        latest_3 = sorted(stable_releases.keys(), reverse=True)[:3]
        stable_versions = [f"stable-{major}.{minor}" for major, minor in latest_3]

        # devel and milestone are required in addition to the actively
        # supported stable branches to comply with the Ansible Community
        # Package inclusion requirements.
        return ["devel", "milestone"] + stable_versions


class GrafanaReleases(GitHubReleases):
    def normalize_version(self, version):
        if version.startswith("v"):
            version = version[1:]
        return tuple(map(int, version.split(".")))

    def get_by_major(self, version):
        version = version.lstrip("v")
        return int(version.split(".")[0]), version, self.normalize_version(version)

    def get_latest_versions(self):
        releases = self.fetch_releases()
        by_major = {}

        for release in releases:
            tag_name = release.get("tag_name", "")
            if release.get("prerelease") or any(c in tag_name for c in "-+"):
                continue
            major, version, as_tuple = self.get_by_major(tag_name)
            if major not in by_major or by_major[major]["as_tuple"] < as_tuple:
                by_major[major] = {"version": version, "as_tuple": as_tuple}

        latest_3_majors = sorted(by_major.keys(), reverse=True)[:3]
        latest_releases = [by_major[major]["version"] for major in latest_3_majors]

        return latest_releases


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("grafana", "ansible"):
        print("Usage: find_versions.py [grafana|ansible]", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == "grafana":
        releases_handler = GrafanaReleases("grafana/grafana")
    else:
        releases_handler = AnsibleReleases("ansible/ansible")

    versions = releases_handler.get_latest_versions()
    print(json.dumps(versions))
