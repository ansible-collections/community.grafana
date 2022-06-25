#!/usr/bin/env python3

import json
import requests


def get_by_major(version):
    if version.startswith("v"):
        version = version[1:]
    return (version[0], version, int(version.replace('.', '')))


def get_grafana_releases():
    r = requests.get('https://api.github.com/repos/grafana/grafana/releases', headers={"Accept": "application/vnd.github.v3+json"})
    if r.status_code != 200:
        raise Exception("Failed to get releases from GitHub")
    return r.json()


by_major = {}

if __name__ == "__main__":
    releases = get_grafana_releases()
    for item in releases:
        if item.get("prerelease"):
            continue
        major, version, as_int = get_by_major(item.get("tag_name"))
        if major not in by_major.keys() or by_major[major]["as_int"] < as_int:
            by_major[major] = {"version": version, "as_int": as_int}
    latest_3_majors = sorted(list(by_major.keys()), reverse=True)[:3]

    latest_releases = []
    for idx in latest_3_majors:
        latest_releases.append(by_major[idx]["version"])
    print(json.dumps(latest_releases))
