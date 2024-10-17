#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright: (c) 2023, flkhndlr (@flkhndlr)

from __future__ import absolute_import, division, print_function

DOCUMENTATION = """
module: grafana_silence
author:
  - flkhndlr (@flkhndlr)
version_added: "1.9.0"
short_description: Manage Grafana Silences
description:
  - Create/delete Grafana Silences through the Alertmanager Silence API.
requirements:
  - The Alertmanager API is only available starting Grafana 8 and the module will fail if the server version is lower than version 8.
options:
  org_id:
    description:
      - The Grafana organization ID where the silence will be created or deleted.
      - Not used when I(grafana_api_key) is set, because the grafana_api_key only belongs to one organization.
      - Mutually exclusive with C(org_name).
    default: 1
    type: int
  org_name:
    description:
      - The Grafana organization name where the silence will be created or deleted.
      - Not used when I(grafana_api_key) is set, because the grafana_api_key only belongs to one organization.
      - Mutually exclusive with C(org_id).
    type: str
  comment:
    description:
      - The comment that describes the silence.
    required: true
    type: str
  created_by:
    description:
      - The author that creates the silence.
    required: true
    type: str
  starts_at:
    description:
      - ISO 8601 Timestamp with milliseconds  e.g. "2029-07-29T08:45:45.000Z" when the silence starts.
    type: str
    required: true
  ends_at:
    description:
      - ISO 8601 Timestamp with milliseconds  e.g. "2029-07-29T08:45:45.000Z" when the silence will end.
      - Mutually exclusive with C(duration).
    type: str
  duration:
    description:
      - Duration for the silence in ISO 8601 duration format e.g. "PT10M" for 10 minutes.
      - Mutually exclusive with C(ends_at).
    type: str
  matchers:
    description:
      - List of matchers to select which alerts are affected by the silence.
    type: list
    elements: dict
    required: true
  state:
    description:
      - Delete the first occurrence of a silence with the same settings. Can be "absent" or "present".
    default: present
    type: str
    choices: ["present", "absent"]
  id:
    description:
      - The id of the silence.
    type: str
  skip_version_check:
    description:
      - Skip Grafana version check and try to reach api endpoint anyway.
      - This parameter can be useful if you enabled `hide_version` in grafana.ini
    required: False
    type: bool
    default: False
extends_documentation_fragment:
- community.grafana.basic_auth
- community.grafana.api_key
"""

EXAMPLES = """
---
- name: Create a silence with duration
  community.grafana.grafana_silence:
    grafana_url: "https://grafana.example.com"
    grafana_api_key: "{{ some_api_token_value }}"
    comment: "a test comment"
    created_by: "me"
    starts_at: "2029-07-29T08:45:45.000Z"
    duration: "PT10M"
    matchers:
      - isEqual: true
        isRegex: true
        name: environment
        value: test
    state: present

- name: Delete silence with duration without specifying id
  community.grafana.grafana_silence:
    grafana_url: "https://grafana.example.com"
    grafana_api_key: "{{ some_api_token_value }}"
    comment: "a test comment"
    created_by: "me"
    starts_at: "2029-07-29T08:45:45.000Z"
    duration: "PT10M"
    matchers:
      - isEqual: true
        isRegex: true
        name: environment
        value: test
    state: absent

- name: Delete silence without specifying id
  community.grafana.grafana_silence:
    grafana_url: "https://grafana.example.com"
    grafana_api_key: "{{ some_api_token_value }}"
    comment: "a test comment"
    created_by: "me"
    starts_at: "2029-07-29T08:45:45.000Z"
    ends_at: "2029-07-29T08:55:45.000Z"
    matchers:
      - isEqual: true
        isRegex: true
        name: environment
        value: test
    state: absent

- name: Create a silence with specified id
  community.grafana.grafana_silence:
    grafana_url: "https://grafana.example.com"
    grafana_api_key: "{{ some_api_token_value }}"
    comment: "a test comment"
    created_by: "me"
    starts_at: "2029-07-29T08:45:45.000Z"
    ends_at: "2029-07-29T08:55:45.000Z"
    matchers:
      - isEqual: true
        isRegex: true
        name: environment
        value: test
    id: "custom-silence-id"
    state: present

- name: Delete a silence by id
  community.grafana.grafana_silence:
    grafana_url: "https://grafana.example.com"
    grafana_api_key: "{{ some_api_token_value }}"
    id: "custom-silence-id"
    state: absent
"""

RETURN = """
---
silence:
  description: Information about the silence
  returned: On success
  type: complex
  contains:
    id:
      description: The id of the silence
      returned: success
      type: str
      sample:
        - ec27df6b-ac3c-412f-ae0b-6e3e1f41c9c3
    comment:
      description: The comment of the silence
      returned: success
      type: str
      sample:
        - this is a test
    createdBy:
      description: The author of the silence
      returned: success
      type: str
      sample:
        - me
    startsAt:
      description: The begin timestamp of the silence
      returned: success
      type: str
      sample:
        - "2029-07-29T08:45:45.000Z"
    endsAt:
      description: The end timestamp of the silence
      returned: success
      type: str
      sample:
        - "2029-07-29T08:55:45.000Z"
    matchers:
      description: The matchers of the silence
      returned: success
      type: list
      sample:
        - [{"isEqual": true, "isRegex": true, "name": "environment", "value": "test"}]
    status:
      description: The status of the silence
      returned: success
      type: dict
      sample:
        - {"state": "pending"}
    updatedAt:
      description: The timestamp of the last update for the silence
      returned: success
      type: str
      sample:
        - "2023-07-27T13:27:33.042Z"
"""

import json
from datetime import datetime, timedelta

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url, basic_auth_header
from ansible.module_utils._text import to_text
from ansible_collections.community.grafana.plugins.module_utils import base

__metaclass__ = type


class GrafanaError(Exception):
    pass


class GrafanaSilenceInterface(object):
    def __init__(self, module):
        self._module = module
        self.grafana_url = base.clean_url(module.params.get("url"))
        self.org_id = None
        # {{{ Authentication header
        self.headers = {"Content-Type": "application/json"}
        if module.params.get("grafana_api_key", None):
            self.headers["Authorization"] = (
                "Bearer %s" % module.params["grafana_api_key"]
            )
        else:
            self.headers["Authorization"] = basic_auth_header(
                module.params["url_username"], module.params["url_password"]
            )
            self.org_id = (
                self.organization_by_name(module.params["org_name"])
                if module.params["org_name"]
                else module.params["org_id"]
            )
            self.switch_organization(self.org_id)
        # }}}

        if module.params.get("skip_version_check") is False:
            try:
                grafana_version = self.get_version()
            except GrafanaError as e:
                self._module.fail_json(failed=True, msg=to_text(e))
            if grafana_version["major"] < 8:
                self._module.fail_json(
                    failed=True,
                    msg="Silences API is available starting with Grafana v8",
                )

    def _send_request(self, url, data=None, headers=None, method="GET"):
        if data is not None:
            data = json.dumps(data)
        if not headers:
            headers = []

        full_url = "{grafana_url}{path}".format(grafana_url=self.grafana_url, path=url)
        resp, info = fetch_url(
            self._module, full_url, data=data, headers=headers, method=method
        )
        status_code = info["status"]
        if status_code == 404:
            return None
        elif status_code == 401:
            self._module.fail_json(
                failed=True,
                msg="Unauthorized to perform action '%s' on '%s'" % (method, full_url),
            )
        elif status_code == 403:
            self._module.fail_json(failed=True, msg="Permission Denied")
        elif status_code in [200, 202]:
            return self._module.from_json(resp.read())
        elif status_code == 400:
            self._module.fail_json(failed=True, msg=info)
        self._module.fail_json(
            failed=True, msg="Grafana Silences API answered with HTTP %d" % status_code
        )

    def switch_organization(self, org_id):
        url = "/api/user/using/%d" % org_id
        self._send_request(url, headers=self.headers, method="POST")

    def organization_by_name(self, org_name):
        url = "/api/user/orgs"
        organizations = self._send_request(url, headers=self.headers, method="GET")
        orga = next((org for org in organizations if org["name"] == org_name))
        if orga:
            return orga["orgId"]

        return self._module.fail_json(
            failed=True, msg="Current user isn't member of organization: %s" % org_name
        )

    def get_version(self):
        url = "/api/health"
        response = self._send_request(
            url, data=None, headers=self.headers, method="GET"
        )
        version = response.get("version")
        if version is not None:
            major, minor, rev = version.split(".")
            return {"major": int(major), "minor": int(minor), "rev": int(rev)}
        raise GrafanaError("Failed to retrieve version from '%s'" % url)

    def create_silence(self, silence):
        url = "/api/alertmanager/grafana/api/v2/silences"
        response = self._send_request(
            url, data=silence, headers=self.headers, method="POST"
        )
        if self.get_version()["major"] == 8:
            response["silenceID"] = response["id"]
            response.pop("id", None)
        return response

    def get_silence(self, silence):
        if silence["silenceID"]:
            url = "/api/alertmanager/grafana/api/v2/silence/%s" % silence["silenceID"]
            response = self._send_request(url, headers=self.headers, method="GET")
            return response
        else:
            url = "/api/alertmanager/grafana/api/v2/silences"
            response = self._send_request(url, headers=self.headers, method="GET")

            for resp in response:
                if (
                    resp["comment"] == silence["comment"]
                    and resp["createdBy"] == silence["createdBy"]
                    and resp["startsAt"] == silence["startsAt"]
                    and resp["endsAt"] == silence["endsAt"]
                    and resp["matchers"] == silence["matchers"]
                ):
                    return resp
            return None

    def delete_silence(self, silence_id):
        url = "/api/alertmanager/grafana/api/v2/silence/{SilenceId}".format(
            SilenceId=silence_id
        )
        response = self._send_request(url, headers=self.headers, method="DELETE")
        return response


def setup_module_object():
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=base.grafana_required_together(),
        mutually_exclusive=base.grafana_mutually_exclusive()
        + [
            ["ends_at", "duration"],
        ],
    )
    return module


argument_spec = base.grafana_argument_spec()
argument_spec.update(
    comment=dict(type="str", required=True),
    created_by=dict(type="str", required=True),
    duration=dict(type="str"),
    ends_at=dict(type="str"),
    id=dict(type="str"),
    matchers=dict(type="list", elements="dict", required=True),
    org_id=dict(default=1, type="int"),
    org_name=dict(type="str"),
    skip_version_check=dict(type="bool", default=False),
    starts_at=dict(type="str", required=True),
    state=dict(type="str", choices=["present", "absent"], default="present"),
)


def parse_iso8601_duration(duration):
    # Remove the leading 'P' and split days ('D'), hours ('H'), minutes ('M')
    duration = duration[1:]  # Remove 'P'
    days, time = duration.split("T") if "T" in duration else (None, duration)

    days = int(days[:-1]) if days and "D" in days else 0
    hours = int(time.split("H")[0][:-1]) if "H" in time else 0
    minutes = int(time.split("M")[0][-1:]) if "M" in time else 0

    return timedelta(days=days, hours=hours, minutes=minutes)


def main():
    module = setup_module_object()
    grafana_iface = GrafanaSilenceInterface(module)
    changed = False
    failed = False

    silence_payload = {
        "comment": module.params.get("comment"),
        "createdBy": module.params.get("created_by"),
        "matchers": module.params.get("matchers"),
        "startsAt": module.params.get("starts_at"),
        "silenceID": module.params.get("silence_id"),
    }

    state = module.params.get("state")

    if module.params.get("ends_at"):
        silence_payload["endsAt"] = module.params.get("ends_at")
    elif module.params.get("duration"):
        starts_at = module.params.get("starts_at")
        duration = module.params.get("duration")

        # Parse starts_at into datetime object
        starts_at_dt = datetime.strptime(starts_at, "%Y-%m-%dT%H:%M:%S.%fZ")

        # Parse ISO 8601 duration into timedelta
        duration_timedelta = parse_iso8601_duration(duration)

        # Calculate ends_at
        ends_at_dt = starts_at_dt + duration_timedelta

        # Format ends_at as ISO 8601
        silence_payload["endsAt"] = ends_at_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    silence = grafana_iface.get_silence(silence_payload)

    if state == "present":
        if not silence:
            silence = grafana_iface.create_silence(silence_payload)
            silence = grafana_iface.get_silence(silence_payload)
            changed = True
        else:
            module.exit_json(
                failed=failed,
                changed=changed,
                msg="Silence with same parameters already exists! eg. '%s'"
                % silence["id"],
            )
    elif state == "absent":
        if silence:
            grafana_iface.delete_silence(silence["id"])
            changed = True
        else:
            module.exit_json(
                failed=False,
                changed=changed,
                msg="Silence does not exist",
            )

    module.exit_json(failed=failed, changed=changed, silence=silence)


if __name__ == "__main__":
    main()
