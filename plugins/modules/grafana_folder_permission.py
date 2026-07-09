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
# along with Ansible. If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function

DOCUMENTATION = '''
---
module: grafana_folder_permissions
author:
  - G3S team
version_added: "1.5.4-g3s-1"
short_description: Manage Grafana Folders Permissions
description:
  - Create/delete Grafana Folders Permissions the Folders Permission API.
requirements:
  - The Folders Permission API is only available starting Grafana 6 and the module will fail if the server version is lower than version 6.
options:
  state:
    description:
      - State of permission for the folder
    default: present
    type: str
    choices: ["present", "absent"]
  folder:
    description:
      - Folder name to apply permission
    required: true
    type: str
  team:
    description:
      - Team name to apply permission
    type: str
  user:
    description:
      - User name to apply permission
    type: str
  role:
    description:
      - User name to apply permission
    type: str
    choices: ['Admin', 'Viewer', 'Editor']
  permission:
    description:
      - User name to apply permission
    type: str
    choices: ['view', 'edit', 'admin']
    required: true
extends_documentation_fragment:
- community.grafana.basic_auth
- community.grafana.api_key
'''

EXAMPLES = '''
---
- name: Set view permission for user that have the role viewer
  community.grafana.grafana_folder_permission:
      url: "https://grafana.example.com"
      grafana_api_key: "{{ some_api_token_value }}"
      folder: "folder"
      role: "Viewer"
      permission: "view"
      state: present

- name: Set edit permission for team "justice league"
  community.grafana.grafana_folder_permission:
      url: "https://grafana.example.com"
      grafana_api_key: "{{ some_api_token_value }}"
      folder: "folder"
      team: "justice league"
      permission: "edit"

- name: Remove admin permission for user "batman"
  community.grafana.grafana_folder_permission:
      url: "https://grafana.example.com"
      grafana_api_key: "{{ some_api_token_value }}"
      folder: "folder"
      user: "batman"
      permission: "admin"
      state: absent
'''

RETURN = '''
---
folder:
    description: Information about the Folder permission
    returned: always
    type: complex
    contains:
        uid:
            description: The Folder uid
            returned: always
            type: str
            sample: "nErXDvCkzz"
        title:
            description: The Folder title
            returned: always
            type: str
            sample: "Department ABC"
        url:
            description: The Folder url
            returned: always
            type: str
            sample: "/dashboards/f/nErXDvCkzz/department-abc"
        created:
            description: The folder creation date
            returned: always
            type: str
            sample: "2018-01-31T17:43:12+01:00"
        updated:
            description: The date the folder was last updated
            returned: always
            type: str
            sample: "2018-01-31T17:43:12+01:00"
        folderId:
            description: The Folder identifier
            returned: always
            type: int
            sample: 5
        inherited:
            description: Is folder inherite parent folder permission
            returned: always
            type: boolean
            sample: false
        isFolder:
            description: Is the permission apply to a folder object
            returned: always
            type: boolean
            sample: true
        permission:
            description: Permission level (1=View, 2=Edit, 4=Admin)
            returned: always
            type: int
            sample: 1
        permissionName:
            description: Permission name
            returned: always
            type: str
            sample: "View"
        role:
            description: Role applied to the permission
            returned: always
            type: str
            sample: "Viewer"
        slug:
            description: Url slug
            returned: always
            type: str
            sample: "department-abc"
        team:
            description: Team name applied to the permission
            returned: always
            type: str
            sample: "team"
        teamAvatarUrl:
            description: Team avatar url applied to the permission
            returned: always
            type: str
            sample: "http://avatar/url"
        teamEmail:
            description: Team email applied to the permission
            returned: always
            type: str
            sample: "team@email.com"
        teamId:
            description: Team id applied to the permission
            returned: always
            type: int
            sample: 1
        userAvatarUrl:
            description: User avatar url applied to the permission
            returned: always
            type: str
            sample: "http://avatar/url"
        userEmail:
            description: User email applied to the permission
            returned: always
            type: str
            sample: "user@email.com"
        userId:
            description: User id applied to the permission
            returned: always
            type: int
            sample: 1
        userLogin:
            description: User login applied to the permission
            returned: always
            type: str
            sample: "foo"
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url, basic_auth_header
from ansible_collections.community.grafana.plugins.module_utils import base
from ansible.module_utils.six.moves.urllib.parse import quote
from ansible.module_utils._text import to_text

__metaclass__ = type


class GrafanaError(Exception):
    pass


class GrafanaFolderPermissionInterface(object):

    def __init__(self, module):
        self._module = module
        # {{{ Authentication header
        self.headers = {"Content-Type": "application/json"}
        if module.params.get('grafana_api_key', None):
            self.headers["Authorization"] = "Bearer %s" % module.params['grafana_api_key']
        else:
            self.headers["Authorization"] = basic_auth_header(module.params['url_username'], module.params['url_password'])
        # }}}
        self.grafana_url = base.clean_url(module.params.get("url"))
        if module.params.get("skip_version_check") is False:
            try:
                grafana_version = self.get_version()
            except GrafanaError as e:
                self._module.fail_json(failed=True, msg=to_text(e))
            if grafana_version["major"] < 6:
                self._module.fail_json(failed=True, msg="Folders API is available starting Grafana v6")

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
        elif status_code == 200:
            return self._module.from_json(resp.read())
        self._module.fail_json(failed=True, msg="Grafana API answered with HTTP %d on %s" % (status_code, full_url))

    def _permission_mapping(self, permission):
        permission_mapping = {
            "view": 1,
            "edit": 2,
            "admin": 4
        }
        permission_id = permission_mapping.get(permission)
        return permission_id

    def _entity_request_mapping(self, entity):
        entity_request_mapping = {
            "role": "role",
            "team": "teamId",
            "user": "userId"
        }
        entity_request = entity_request_mapping.get(entity)
        return entity_request

    def _request_with_current_permission(self, folder):
        request_permission = {"items": []}
        for item in self.get_folder_permission(folder):
            merged_item = {}
            if item['userId'] > 0:
                merged_item['userId'] = item['userId']
            if item['teamId'] > 0:
                merged_item['teamId'] = item['teamId']
            if 'role' in item:
                merged_item['role'] = item['role']
            merged_item['permission'] = item['permission']
            request_permission["items"].append(merged_item)

        return request_permission

    def get_version(self):
        url = "/api/health"
        response = self._send_request(url, data=None, headers=self.headers, method="GET")
        version = response.get("version")
        if version is not None:
            major, minor, rev = version.split(".")
            return {"major": int(major), "minor": int(minor), "rev": int(rev)}
        raise GrafanaError("Failed to retrieve version from '%s'" % url)

    def get_folder(self, title):
        url = "/api/search?type=dash-folder&query={title}".format(title=quote(title))
        response = self._send_request(url, headers=self.headers, method="GET")
        for item in response:
            if item.get("title") == to_text(title):
                return item['uid']

    def get_folder_permission(self, title_id):
        url = "/api/folders/{title_id}/permissions".format(title_id=title_id)
        response = self._send_request(url, headers=self.headers, method="GET")
        return response

    def check_permission_exists(self, folder_uid, entity, permission, entity_id):

        permission_id = self._permission_mapping(permission)
        entity_request = self._entity_request_mapping(entity)

        folder_permissions = self.get_folder_permission(folder_uid)
        return any(
            item.get(entity_request, None) == entity_id and item['permission'] == permission_id
            for item in folder_permissions
        )

    def get_team(self, name):
        url = "/api/teams/search?name={team}".format(team=quote(name))
        response = self._send_request(url, headers=self.headers, method="GET")
        if not response.get("totalCount") <= 1:
            raise AssertionError("Expected 1 team, got %d" % response["totalCount"])
        if len(response.get("teams")) == 0:
           self._module.fail_json(failed=True, msg="Team does not exist")
        return response.get("teams")[0]['id']

    def get_user_from_login(self, login):
        url = "/api/users/lookup?loginOrEmail={login}".format(login=quote(login))
        response = self._send_request(url, headers=self.headers, method="GET")
        if not response:
            self._module.fail_json(failed=True, msg="User does not exist")
        return response['id']

    def create_folder_permission(self, folder_uid, entity, permission, entity_id):
        url = "/api/folders/{folder_uid}/permissions".format(folder_uid=folder_uid)

        permission_id = self._permission_mapping(permission)
        entity_request = self._entity_request_mapping(entity)

        new_permission = {entity_request: entity_id, "permission": permission_id}
        request_permission = self._request_with_current_permission(folder_uid)
        request_permission["items"] = [item for item in request_permission["items"] if item.get(entity_request, None) != entity_id]
        request_permission["items"].append(new_permission)
        response = self._send_request(url, data=request_permission, headers=self.headers, method="POST")

        return response

    def delete_folder_permission(self, folder_uid, entity, permission, entity_id):
        url = "/api/folders/{folder_uid}/permissions".format(folder_uid=folder_uid)

        permission_id = self._permission_mapping(permission)
        entity_request = self._entity_request_mapping(entity)
        permission_to_remove = {entity_request: entity_id, "permission": permission_id}
        request_permission = self._request_with_current_permission(folder_uid)
        request_permission["items"].remove(permission_to_remove)
        response = self._send_request(url, data=request_permission, headers=self.headers, method="POST")

        return response

def present_folder_permission(grafana_iface, folder_uid, entity, permission, entity_id):
    if not grafana_iface.check_permission_exists(folder_uid, entity, permission, entity_id):
        grafana_iface.create_folder_permission(folder_uid, entity, permission, entity_id)
        return True
    return False

def remove_folder_permission(grafana_iface, folder_uid, entity, permission, entity_id):
    if grafana_iface.check_permission_exists(folder_uid, entity, permission, entity_id):
        grafana_iface.delete_folder_permission(folder_uid, entity, permission, entity_id)
        return True
    return False

def main():

    argument_spec = base.grafana_argument_spec()
    argument_spec.update(
        state=dict(type='str', default='present', choices=['present', 'absent']),
        folder=dict(type='str', required=True),
        team=dict(type='str'),
        user=dict(type='str'),
        role=dict(type='str', choices=['Admin', 'Viewer', 'Editor']),
        permission=dict(type='str', required=True, choices=['view', 'edit', 'admin']),
        )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_if=[
            ['state', 'export', ['path']],
        ],
        required_together=[['url_username', 'url_password']],
        mutually_exclusive=[
            ['url_username', 'grafana_api_key'],
            ['uid', 'slug'],
            ['path', 'dashboard_id'],
            ['team', 'user', 'role']
        ],
    )
    state = module.params['state']
    folder = module.params['folder']
    team = module.params['team']
    user = module.params['user']
    role = module.params['role']
    permission = module.params['permission']

    grafana_iface = GrafanaFolderPermissionInterface(module)

    folder_uid = grafana_iface.get_folder(folder)
    changed = False
    if team is not None:
        entity_type = 'team'
        entity_id = grafana_iface.get_team(team)
    elif user is not None:
        entity_type = 'user'
        entity_id = grafana_iface.get_user_from_login(user)
    elif role is not None:
        entity_type = 'role'
        entity_id = role

    if state == 'present':
        changed = present_folder_permission(grafana_iface, folder_uid, entity_type, permission, entity_id)
    elif state == 'absent':
        changed = remove_folder_permission(grafana_iface, folder_uid, entity_type, permission, entity_id)

    folder_permission = grafana_iface.get_folder_permission(folder_uid)
    module.exit_json(changed=changed, folder_permission=folder_permission)

if __name__ == '__main__':
    main()
