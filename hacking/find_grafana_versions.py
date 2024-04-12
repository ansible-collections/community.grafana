#!/usr/bin/env python

import json
import requests


def get_by_major(version):
    if version.startswith("v"):
        version = version[1:]
    return int(version.split(".")[0]), version, tuple(map(int, version.split(".")))


def get_grafana_releases():
    r = requests.get(
        "https://api.github.com/repos/grafana/grafana/releases?per_page=100",
        headers={"Accept": "application/vnd.github.v3+json"},
    )
    if r.status_code != 200:
        raise Exception("Failed to get releases from GitHub")
    return r.json()


if __name__ == "__main__":
    releases = get_grafana_releases()
    by_major = {}

    for release in releases:
        if release.get("prerelease") or any(
            char in release.get("tag_name") for char in "-+"
        ):
            continue
        major, version, as_tuple = get_by_major(release.get("tag_name"))
        if major not in by_major.keys() or by_major[major]["as_tuple"] < as_tuple:
            by_major[major] = {"version": version, "as_tuple": as_tuple}

    latest_3_majors = sorted(list(by_major.keys()))[:3]
    latest_releases = [by_major[idx]["version"] for idx in latest_3_majors]

    print(json.dumps(latest_releases))
