#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Thierry Sallé (@seuf)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

ANSIBLE_METADATA = {
    'status': ['preview'],
    'supported_by': 'community',
    'metadata_version': '1.1'
}

DOCUMENTATION = '''
---
module: grafana_dashboard
author:
  - Thierry Sallé (@seuf)
version_added: "2.5"
short_description: Manage Grafana dashboards
description:
  - Create, update, delete, export Grafana dashboards via API.
options:
  org_id:
    description:
      - The Grafana Organisation ID where the dashboard will be imported / exported.
      - Not used when I(grafana_api_key) is set, because the grafana_api_key only belongs to one organisation..
    default: 1
  folder:
    description:
      - The Grafana folder where this dashboard will be imported to.
    default: General
    version_added: '2.10'
  state:
    description:
      - State of the dashboard.
    choices: [ absent, export, present ]
    default: present
  slug:
    description:
      - Deprecated since Grafana 5. Use grafana dashboard uid instead.
      - slug of the dashboard. It's the friendly url name of the dashboard.
      - When C(state) is C(present), this parameter can override the slug in the meta section of the json file.
      - If you want to import a json dashboard exported directly from the interface (not from the api),
        you have to specify the slug parameter because there is no meta section in the exported json.
  uid:
    version_added: 2.7
    description:
      - uid of the dashboard to export when C(state) is C(export) or C(absent).
  path:
    description:
      - The path to the json file containing the Grafana dashboard to import or export.
      - A http URL is also accepted (since 2.10).
    aliases: [ dashboard_url ]
  overwrite:
    description:
      - Override existing dashboard when state is present.
    type: bool
    default: 'no'
  dashboard_id:
    description:
      - Public Grafana.com dashboard id to import
    version_added: '2.10'
  dashboard_revision:
    description:
      - Revision of the public grafana dashboard to import
    default: 1
    version_added: '2.10'
  message:
    description:
      - Set a commit message for the version history.
      - Only used when C(state) is C(present).
extends_documentation_fragment:
- ansible_collections.grafana.grafana
'''

EXAMPLES = '''
- hosts: localhost
  connection: local
  tasks:
    - name: Import Grafana dashboard foo
      grafana_dashboard:
        grafana_url: http://grafana.company.com
        grafana_api_key: "{{ grafana_api_key }}"
        state: present
        message: Updated by ansible
        overwrite: yes
        path: /path/to/dashboards/foo.json

    - name: Import Grafana dashboard Zabbix
      grafana_dashboard:
        grafana_url: http://grafana.company.com
        grafana_api_key: "{{ grafana_api_key }}"
        folder: zabbix
        dashboard_id: 6098
        dashbord_revision: 1

    - name: Import Grafana dashboard zabbix
      grafana_dashboard:
        grafana_url: http://grafana.company.com
        grafana_api_key: "{{ grafana_api_key }}"
        folder: public
        dashboard_url: https://grafana.com/api/dashboards/6098/revisions/1/download

    - name: Export dashboard
      grafana_dashboard:
        grafana_url: http://grafana.company.com
        grafana_user: "admin"
        grafana_password: "{{ grafana_password }}"
        org_id: 1
        state: export
        uid: "000000653"
        path: "/path/to/dashboards/000000653.json"
'''

RETURN = '''
---
uid:
  description: uid or slug of the created / deleted / exported dashboard.
  returned: success
  type: str
  sample: 000000063
'''

import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils._text import to_native
from ansible.module_utils._text import to_text
from ansible_collections.gundalow_collections.grafana.plugins.module_utils.base import grafana_argument_spec

__metaclass__ = type


class GrafanaAPIException(Exception):
    pass


class GrafanaMalformedJson(Exception):
    pass


class GrafanaExportException(Exception):
    pass


class GrafanaDeleteException(Exception):
    pass


def grafana_switch_organisation(module, grafana_url, org_id, headers):
    r, info = fetch_url(module, '%s/api/user/using/%s' % (grafana_url, org_id), headers=headers, method='POST')
    if info['status'] != 200:
        raise GrafanaAPIException('Unable to switch to organization %s : %s' % (org_id, info))


def grafana_headers(module, data):
    headers = {'content-type': 'application/json; charset=utf8'}
    if 'grafana_api_key' in data and data['grafana_api_key']:
        headers['Authorization'] = "Bearer %s" % data['grafana_api_key']
    else:
        module.params['force_basic_auth'] = True
        grafana_switch_organisation(module, data['grafana_url'], data['org_id'], headers)

    return headers


def get_grafana_version(module, grafana_url, headers):
    grafana_version = None
    r, info = fetch_url(module, '%s/api/frontend/settings' % grafana_url, headers=headers, method='GET')
    if info['status'] == 200:
        try:
            settings = json.loads(to_text(r.read()))
            grafana_version = settings['buildInfo']['version'].split('.')[0]
        except UnicodeError as e:
            raise GrafanaAPIException('Unable to decode version string to Unicode')
        except Exception as e:
            raise GrafanaAPIException(e)
    else:
        raise GrafanaAPIException('Unable to get grafana version : %s' % info)

    return int(grafana_version)


def grafana_folder_exists(module, grafana_url, folder_name, headers):
    # the 'General' folder is a special case, it's ID is always '0'
    if folder_name == 'General':
        return True, 0

    try:
        r, info = fetch_url(module, '%s/api/folders' % grafana_url, headers=headers, method='GET')

        if info['status'] != 200:
            raise GrafanaAPIException("Unable to query Grafana API for folders (name: %s): %d" % (folder_name, info['status']))

        folders = json.loads(r.read())

        for folder in folders:
            if folder['title'] == folder_name:
                return True, folder['id']
    except Exception as e:
        raise GrafanaAPIException(e)

    return False, 0


def grafana_dashboard_exists(module, grafana_url, uid, headers):
    dashboard_exists = False
    dashboard = {}

    grafana_version = get_grafana_version(module, grafana_url, headers)
    if grafana_version >= 5:
        uri = '%s/api/dashboards/uid/%s' % (grafana_url, uid)
    else:
        uri = '%s/api/dashboards/db/%s' % (grafana_url, uid)

    r, info = fetch_url(module, uri, headers=headers, method='GET')

    if info['status'] == 200:
        dashboard_exists = True
        try:
            dashboard = json.loads(r.read())
        except Exception as e:
            raise GrafanaAPIException(e)
    elif info['status'] == 404:
        dashboard_exists = False
    else:
        raise GrafanaAPIException('Unable to get dashboard %s : %s' % (uid, info))

    return dashboard_exists, dashboard


def grafana_dashboard_search(module, grafana_url, folder_id, title, headers):

    # search by title
    uri = '%s/api/search?%s' % (grafana_url, urlencode({
        'folderIds': folder_id,
        'query': title,
        'type': 'dash-db'
    }))
    r, info = fetch_url(module, uri, headers=headers, method='GET')

    if info['status'] == 200:
        try:
            dashboards = json.loads(r.read())
            for d in dashboards:
                if d['title'] == title:
                    return grafana_dashboard_exists(module, grafana_url, d['uid'], headers)
        except Exception as e:
            raise GrafanaAPIException(e)
    else:
        raise GrafanaAPIException('Unable to search dashboard %s : %s' % (title, info))

    return False, None


# for comparison, we sometimes need to ignore a few keys
def grafana_dashboard_changed(payload, dashboard):
    # you don't need to set the version, but '0' is incremented to '1' by Grafana's API
    if payload['dashboard']['version'] == 0:
        del(payload['dashboard']['version'])
        del(dashboard['dashboard']['version'])

    # the meta key is not part of the 'payload' ever
    if 'meta' in dashboard:
        del(dashboard['meta'])

    # new dashboards don't require an id attribute (or, it can be 'null'), Grafana's API will generate it
    if payload['dashboard'].get('id'):
        del(dashboard['dashboard']['id'])
        del(payload['dashboard']['id'])

    if payload == dashboard:
        return True

    return False


def grafana_create_dashboard(module, data):

    # define data payload for grafana API
    payload = {}
    if data.get('dashboard_id'):
        data['path'] = "https://grafana.com/api/dashboards/%s/revisions/%s/download" % (data['dashboard_id'], data['dashboard_revision'])
    if data['path'].startswith('http'):
        r, info = fetch_url(module, data['path'])
        if info['status'] != 200:
            raise GrafanaAPIException('Unable to download grafana dashboard from url %s : %s' % (data['path'], info))
        payload = json.loads(r.read())
    else:
        try:
            with open(data['path'], 'r') as json_file:
                payload = json.load(json_file)
        except Exception as e:
            raise GrafanaAPIException("Can't load json file %s" % to_native(e))

    # Check that the dashboard JSON is nested under the 'dashboard' key
    if 'dashboard' not in payload:
        payload = {'dashboard': payload}

    # define http header
    headers = grafana_headers(module, data)

    grafana_version = get_grafana_version(module, data['grafana_url'], headers)
    if grafana_version < 5:
        if data.get('slug'):
            uid = data['slug']
        elif 'meta' in payload and 'slug' in payload['meta']:
            uid = payload['meta']['slug']
        else:
            raise GrafanaMalformedJson('No slug found in json. Needed with grafana < 5')
    else:
        if data.get('uid'):
            uid = data['uid']
        elif 'uid' in payload['dashboard']:
            uid = payload['dashboard']['uid']
        else:
            uid = None

    result = {}

    # test if the folder exists
    if grafana_version >= 5:
        folder_exists, folder_id = grafana_folder_exists(module, data['grafana_url'], data['folder'], headers)
        if folder_exists is False:
            result['msg'] = "Dashboard folder '%s' does not exist." % data['folder']
            result['uid'] = uid
            result['changed'] = False
            return result

        payload['folderId'] = folder_id

    # test if dashboard already exists
    if uid:
        dashboard_exists, dashboard = grafana_dashboard_exists(
            module, data['grafana_url'], uid, headers=headers)
    else:
        dashboard_exists, dashboard = grafana_dashboard_search(
            module, data['grafana_url'], folder_id, payload['dashboard']['title'], headers=headers)

    if dashboard_exists is True:
        if grafana_dashboard_changed(payload, dashboard):
            # update
            if 'overwrite' in data and data['overwrite']:
                payload['overwrite'] = True
            if 'message' in data and data['message']:
                payload['message'] = data['message']

            r, info = fetch_url(module, '%s/api/dashboards/db' % data['grafana_url'],
                                data=json.dumps(payload), headers=headers, method='POST')
            if info['status'] == 200:
                if grafana_version >= 5:
                    try:
                        dashboard = json.loads(r.read())
                        uid = dashboard['uid']
                    except Exception as e:
                        raise GrafanaAPIException(e)
                result['uid'] = uid
                result['msg'] = "Dashboard %s updated" % payload['dashboard']['title']
                result['changed'] = True
            else:
                body = json.loads(info['body'])
                raise GrafanaAPIException('Unable to update the dashboard %s : %s (HTTP: %d)' %
                                          (uid, body['message'], info['status']))
        else:
            # unchanged
            result['uid'] = uid
            result['msg'] = "Dashboard %s unchanged." % payload['dashboard']['title']
            result['changed'] = False
    else:
        # create
        if folder_exists is True:
            payload['folderId'] = folder_id

        # Ensure there is no id in payload
        if 'id' in payload['dashboard']:
            del payload['dashboard']['id']

        r, info = fetch_url(module, '%s/api/dashboards/db' % data['grafana_url'],
                            data=json.dumps(payload), headers=headers, method='POST')
        if info['status'] == 200:
            result['msg'] = "Dashboard %s created" % payload['dashboard']['title']
            result['changed'] = True
            if grafana_version >= 5:
                try:
                    dashboard = json.loads(r.read())
                    uid = dashboard['uid']
                except Exception as e:
                    raise GrafanaAPIException(e)
            result['uid'] = uid
        else:
            raise GrafanaAPIException('Unable to create the new dashboard %s : %s - %s. (headers : %s)' %
                                      (payload['dashboard']['title'], info['status'], info, headers))

    return result


def grafana_delete_dashboard(module, data):

    # define http headers
    headers = grafana_headers(module, data)

    grafana_version = get_grafana_version(module, data['grafana_url'], headers)
    if grafana_version < 5:
        if data.get('slug'):
            uid = data['slug']
        else:
            raise GrafanaMalformedJson('No slug parameter. Needed with grafana < 5')
    else:
        if data.get('uid'):
            uid = data['uid']
        else:
            raise GrafanaDeleteException('No uid specified %s')

    # test if dashboard already exists
    dashboard_exists, dashboard = grafana_dashboard_exists(module, data['grafana_url'], uid, headers=headers)

    result = {}
    if dashboard_exists is True:
        # delete
        if grafana_version < 5:
            r, info = fetch_url(module, '%s/api/dashboards/db/%s' % (data['grafana_url'], uid), headers=headers, method='DELETE')
        else:
            r, info = fetch_url(module, '%s/api/dashboards/uid/%s' % (data['grafana_url'], uid), headers=headers, method='DELETE')
        if info['status'] == 200:
            result['msg'] = "Dashboard %s deleted" % uid
            result['changed'] = True
            result['uid'] = uid
        else:
            raise GrafanaAPIException('Unable to update the dashboard %s : %s' % (uid, info))
    else:
        # dashboard does not exist, do nothing
        result = {'msg': "Dashboard %s does not exist." % uid,
                  'changed': False,
                  'uid': uid}

    return result


def grafana_export_dashboard(module, data):

    # define http headers
    headers = grafana_headers(module, data)

    grafana_version = get_grafana_version(module, data['grafana_url'], headers)
    if grafana_version < 5:
        if data.get('slug'):
            uid = data['slug']
        else:
            raise GrafanaMalformedJson('No slug parameter. Needed with grafana < 5')
    else:
        if data.get('uid'):
            uid = data['uid']
        else:
            raise GrafanaExportException('No uid specified')

    # test if dashboard already exists
    dashboard_exists, dashboard = grafana_dashboard_exists(module, data['grafana_url'], uid, headers=headers)

    if dashboard_exists is True:
        try:
            with open(data['path'], 'w') as f:
                f.write(json.dumps(dashboard))
        except Exception as e:
            raise GrafanaExportException("Can't write json file : %s" % to_native(e))
        result = {'msg': "Dashboard %s exported to %s" % (uid, data['path']),
                  'uid': uid,
                  'changed': True}
    else:
        result = {'msg': "Dashboard %s does not exist." % uid,
                  'uid': uid,
                  'changed': False}

    return result


def main():
    # use the predefined argument spec for url
    argument_spec = grafana_argument_spec()
    argument_spec.update(
        state=dict(choices=['present', 'absent', 'export'], default='present'),
        org_id=dict(default=1, type='int'),
        folder=dict(type='str', default='General'),
        uid=dict(type='str'),
        slug=dict(type='str'),
        path=dict(aliases=['dashboard_url'], type='str'),
        dashboard_id=dict(type='str'),
        dashboard_revision=dict(type='str', default='1'),
        overwrite=dict(type='bool', default=False),
        message=dict(type='str'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[['url_username', 'url_password', 'org_id']],
        mutually_exclusive=[['grafana_user', 'grafana_api_key'], ['uid', 'slug'], ['path', 'dashboard_id']],
    )

    try:
        if module.params['state'] == 'present':
            result = grafana_create_dashboard(module, module.params)
        elif module.params['state'] == 'absent':
            result = grafana_delete_dashboard(module, module.params)
        else:
            result = grafana_export_dashboard(module, module.params)
    except GrafanaAPIException as e:
        module.fail_json(
            failed=True,
            msg="error : %s" % to_native(e)
        )
        return
    except GrafanaMalformedJson as e:
        module.fail_json(
            failed=True,
            msg="error : %s" % to_native(e)
        )
        return
    except GrafanaDeleteException as e:
        module.fail_json(
            failed=True,
            msg="error : Can't delete dashboard : %s" % to_native(e)
        )
        return
    except GrafanaExportException as e:
        module.fail_json(
            failed=True,
            msg="error : Can't export dashboard : %s" % to_native(e)
        )
        return

    module.exit_json(
        failed=False,
        **result
    )
    return


if __name__ == '__main__':
    main()
