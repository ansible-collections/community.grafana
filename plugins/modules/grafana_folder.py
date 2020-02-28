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
# Copyright: (c) 2019, Rémi REY (@rrey)

from __future__ import absolute_import, division, print_function

ANSIBLE_METADATA = {
    'status': ['preview'],
    'supported_by': 'community',
    'metadata_version': '1.1'
}

DOCUMENTATION = '''
---
module: grafana_folder
author:
  - Rémi REY (@rrey)
version_added: "2.10"
short_description: Manage Grafana Folders
description:
  - Create/update/delete Grafana Folders through the Folders API.
  - The Folders API is only available starting Grafana 5 and the module will fail if the server version is lower than version 5.
options:
  name:
    description:
      - The title of the Grafana Folder.
    required: true
    type: str
    aliases: [ title ]
  state:
    description:
      - Delete the members not found in the C(members) parameters from the
      - list of members found on the Folder.
    default: present
    type: str
    choices: ["present", "absent"]
extends_documentation_fragment:
- community.grafana.basic_auth
- community.grafana.api_key
'''

EXAMPLES = '''
---
- name: Create a folder
  grafana_folder:
      url: "https://grafana.example.com"
      grafana_api_key: "{{ some_api_token_value }}"
      title: "grafana_working_group"
      state: present

- name: Delete a folder
  grafana_folder:
      url: "https://grafana.example.com"
      grafana_api_key: "{{ some_api_token_value }}"
      title: "grafana_working_group"
      state: absent
'''

RETURN = '''
---
folder:
    description: Information about the Folder
    returned: On success
    type: complex
    contains:
        id:
            description: The Folder identifier
            returned: always
            type: int
            sample:
              - 42
        uid:
            description: The Folder uid
            returned: always
            type: str
            sample:
              - "nErXDvCkzz"
        title:
            description: The Folder title
            returned: always
            type: str
            sample:
              - "Department ABC"
        url:
            description: The Folder url
            returned: always
            type: str
            sample:
              - "/dashboards/f/nErXDvCkzz/department-abc"
        hasAcl:
            description: Boolean specifying if folder has acl
            returned: always
            type: bool
            sample:
              - false
        canSave:
            description: Boolean specifying if current user can save in folder
            returned: always
            type: bool
            sample:
              - false
        canEdit:
            description: Boolean specifying if current user can edit in folder
            returned: always
            type: bool
            sample:
              - false
        canAdmin:
            description: Boolean specifying if current user can admin in folder
            returned: always
            type: bool
            sample:
              - false
        createdBy:
            description: The name of the user who created the folder
            returned: always
            type: str
            sample:
              - "admin"
        created:
            description: The folder creation date
            returned: always
            type: str
            sample:
              - "2018-01-31T17:43:12+01:00"
        updatedBy:
            description: The name of the user who last updated the folder
            returned: always
            type: str
            sample:
              - "admin"
        updated:
            description: The date the folder was last updated
            returned: always
            type: str
            sample:
              - "2018-01-31T17:43:12+01:00"
        version:
            description: The folder version
            returned: always
            type: int
            sample:
              - 1
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url, basic_auth_header
from ansible_collections.community.grafana.plugins.module_utils.base import grafana_argument_spec, grafana_required_together, grafana_mutually_exclusive

__metaclass__ = type


class GrafanaFolderInterface(object):

    def __init__(self, module):
        self._module = module
        # {{{ Authentication header
        self.headers = {"Content-Type": "application/json"}
        if module.params.get('grafana_api_key', None):
            self.headers["Authorization"] = "Bearer %s" % module.params['grafana_api_key']
        else:
            self.headers["Authorization"] = basic_auth_header(module.params['url_username'], module.params['url_password'])
        # }}}
        self.grafana_url = module.params.get("url")
        grafana_version = self.get_version()
        if grafana_version["major"] < 5:
            self._module.fail_json(failed=True, msg="Folders API is available starting Grafana v5")

    def _send_request(self, url, data=None, headers=None, method="GET"):
        if data is not None:
            data = json.dumps(data, sort_keys=True)
        if not headers:
            headers = []

        full_url = "{grafana_url}{path}".format(grafana_url=self.grafana_url, path=url)
        resp, info = fetch_url(self._module, full_url, data=data, headers=headers, method=method)
        status_code = info["status"]
        if status_code == 404:
            return None
        elif status_code == 401:
            self._module.fail_json(failed=True, msg="Unauthorized to perform action '%s' on '%s'" % (method, full_url))
        elif status_code == 403:
            self._module.fail_json(failed=True, msg="Permission Denied")
        elif status_code == 412:
            error_msg = resp.read()['message']
            self._module.fail_json(failed=True, msg=error_msg)
        elif status_code == 200:
            return self._module.from_json(resp.read())
        self._module.fail_json(failed=True, msg="Grafana Folders API answered with HTTP %d" % status_code)

    def get_version(self):
        url = "/api/health"
        response = self._send_request(url, data=None, headers=self.headers, method="GET")
        version = response.get("version")
        major, minor, rev = version.split(".")
        return {"major": int(major), "minor": int(minor), "rev": int(rev)}

    def create_folder(self, title):
        url = "/api/folders"
        folder = dict(title=title)
        response = self._send_request(url, data=folder, headers=self.headers, method="POST")
        return response

    def get_folder(self, title):
        url = "/api/search?type=dash-folder&query={title}".format(title=title)
        response = self._send_request(url, headers=self.headers, method="GET")
        for item in response:
            if item.get("title") == title:
                return item
        return None

    def delete_folder(self, folder_uid):
        url = "/api/folders/{folder_uid}".format(folder_uid=folder_uid)
        response = self._send_request(url, headers=self.headers, method="DELETE")
        return response


def setup_module_object():
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=grafana_required_together(),
        mutually_exclusive=grafana_mutually_exclusive(),
    )
    return module


argument_spec = grafana_argument_spec()
argument_spec.update(
    name=dict(type='str', aliases=['title'], required=True),
    state=dict(type='str', default='present', choices=['present', 'absent']),
)


def main():

    module = setup_module_object()
    state = module.params['state']
    title = module.params['name']

    grafana_iface = GrafanaFolderInterface(module)

    changed = False
    if state == 'present':
        folder = grafana_iface.get_folder(title)
        if folder is None:
            grafana_iface.create_folder(title)
            folder = grafana_iface.get_folder(title)
            changed = True
        folder = grafana_iface.get_folder(title)
        module.exit_json(changed=changed, folder=folder)
    elif state == 'absent':
        folder = grafana_iface.get_folder(title)
        if folder is None:
            module.exit_json(changed=False, message="No folder found")
        result = grafana_iface.delete_folder(folder.get("uid"))
        module.exit_json(changed=True, message=result)


if __name__ == '__main__':
    main()
