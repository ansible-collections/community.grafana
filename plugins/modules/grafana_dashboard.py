#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Thierry Sallé (@seuf)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

DOCUMENTATION = """
---
module: grafana_dashboard
author:
  - Thierry Sallé (@seuf)
version_added: "1.0.0"
short_description: Manage Grafana dashboards
description:
  - Create, update, delete, export Grafana dashboards via API.
options:
  org_id:
    description:
      - The Grafana organization ID where the dashboard will be imported / exported / deleted.
      - Not used when I(grafana_api_key) is set, because the grafana_api_key only belongs to one organization.
      - Mutually exclusive with C(org_name).
    default: 1
    type: int
  org_name:
    description:
      - The Grafana organization name where the dashboard will be imported / exported / deleted.
      - Not used when I(grafana_api_key) is set, because the grafana_api_key only belongs to one organization.
      - Mutually exclusive with C(org_id).
    type: str
  folder:
    description:
      - UID of the folder where the dashboard will be created or imported.
      - Required if C(parent_folder) is set.
    default: General
    version_added: "1.0.0"
    type: str
  parent_folder:
    description:
      - UID of the parent folder used to scope the search for the specified C(folder).
      - Available with subfolder feature of Grafana 11.
    version_added: "2.2.0"
    type: str
  state:
    description:
      - State of the dashboard.
    choices: [ absent, export, present ]
    default: present
    type: str
  slug:
    description:
      - Deprecated since Grafana 5. Use grafana dashboard uid instead.
      - slug of the dashboard. It's the friendly url name of the dashboard.
      - When C(state) is C(present), this parameter can override the slug in the meta section of the json file.
      - If you want to import a json dashboard exported directly from the interface (not from the api),
        you have to specify the slug parameter because there is no meta section in the exported json.
    type: str
  uid:
    version_added: "1.0.0"
    description:
      - Used to identify the dashboard when C(state) is C(export) or C(absent).
      - When C(state) is C(present), this can be used to set the UID during dashboard creation.
    type: str
  path:
    description:
      - The path to the json file containing the Grafana dashboard to import or export.
      - A http URL is also accepted (since 2.10).
      - Required if C(state) is C(export) or C(present).
    aliases: [ dashboard_url ]
    type: str
  namespace:
    description:
      - The namespace of the dashboard to export or import.
      - Only used when C(api_version) is C(v2).
    default: default
    type: str
  api_version:
    description:
      - API version to use when interacting with Grafana.
    choices: [ v1, v2 ]
    default: v1
    type: str
  overwrite:
    description:
      - Override existing dashboard when state is present.
    type: bool
    default: false
  dashboard_id:
    description:
      - Public Grafana.com dashboard id to import
    version_added: "1.0.0"
    type: str
  dashboard_revision:
    description:
      - Revision of the public grafana dashboard to import
    default: '1'
    version_added: "1.0.0"
    type: str
  commit_message:
    description:
      - Set a commit message for the version history.
      - Only used when C(state) is C(present).
    type: str
extends_documentation_fragment:
- community.grafana.basic_auth
- community.grafana.api_key
"""

EXAMPLES = """
- name: Import Grafana dashboard foo
  community.grafana.grafana_dashboard:
    grafana_url: http://grafana.company.com
    grafana_api_key: "{{ grafana_api_key }}"
    state: present
    commit_message: Updated by ansible
    overwrite: true
    path: /path/to/dashboards/foo.json

- name: Import Grafana dashboard Zabbix
  community.grafana.grafana_dashboard:
    grafana_url: http://grafana.company.com
    grafana_api_key: "{{ grafana_api_key }}"
    folder: zabbix
    dashboard_id: 6098
    dashboard_revision: 1

- name: Import Grafana dashboard zabbix
  community.grafana.grafana_dashboard:
    grafana_url: http://grafana.company.com
    grafana_api_key: "{{ grafana_api_key }}"
    folder: public
    dashboard_url: https://grafana.com/api/dashboards/6098/revisions/1/download

- name: Import Grafana dashboard zabbix in a subfolder
  community.grafana.grafana_dashboard:
    grafana_url: http://grafana.company.com
    grafana_api_key: "{{ grafana_api_key }}"
    parent_folder: public
    folder: myteam
    dashboard_url: https://grafana.com/api/dashboards/6098/revisions/1/download

- name: Export dashboard
  community.grafana.grafana_dashboard:
    grafana_url: http://grafana.company.com
    grafana_user: "admin"
    grafana_password: "{{ grafana_password }}"
    org_id: 1
    state: export
    uid: "000000653"
    path: "/path/to/dashboards/000000653.json"

- name: Export dashboard in v2 format
  community.grafana.grafana_dashboard:
    grafana_url: http://grafana.company.com
    grafana_user: "admin"
    grafana_password: "{{ grafana_password }}"
    org_id: 1
    state: export
    uid: "000000653"
    path: "/path/to/dashboards/000000653.json"
    api_version: v2
"""

RETURN = """
---
uid:
  description: uid or slug of the created / deleted / exported dashboard.
  returned: success
  type: str
  sample: 000000063
"""

import json
import yaml
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils._text import to_native
from ansible.module_utils._text import to_text
from ansible_collections.community.grafana.plugins.module_utils.base import (
    grafana_argument_spec,
    clean_url,
    parse_grafana_version,
)

__metaclass__ = type


class GrafanaAPIException(Exception):
    pass


class GrafanaMalformedJson(Exception):
    pass


class GrafanaExportException(Exception):
    pass


class GrafanaDeleteException(Exception):
    pass


def grafana_organization_id_by_name(module, grafana_url, org_name, headers):
    r, info = fetch_url(
        module, "%s/api/user/orgs" % grafana_url, headers=headers, method="GET"
    )
    if info["status"] != 200:
        raise GrafanaAPIException("Unable to retrieve users organizations: %s" % info)
    organizations = json.loads(to_text(r.read()))
    for org in organizations:
        if org["name"] == org_name:
            return org["orgId"]

    raise GrafanaAPIException(
        "Current user isn't member of organization: %s" % org_name
    )


def grafana_switch_organization(module, grafana_url, org_id, headers):
    r, info = fetch_url(
        module,
        "%s/api/user/using/%s" % (grafana_url, org_id),
        headers=headers,
        method="POST",
    )
    if info["status"] != 200:
        raise GrafanaAPIException(
            "Unable to switch to organization %s : %s" % (org_id, info)
        )


def grafana_headers(module, data):
    headers = {"content-type": "application/json; charset=utf8"}
    if "grafana_api_key" in data and data["grafana_api_key"]:
        headers["Authorization"] = "Bearer %s" % data["grafana_api_key"]
    else:
        module.params["force_basic_auth"] = True
        if module.params["org_name"]:
            org_name = module.params["org_name"]
            data["org_id"] = grafana_organization_id_by_name(
                module, data["url"], org_name, headers
            )
        grafana_switch_organization(module, data["url"], data["org_id"], headers)

    return headers


def get_grafana_version(module, grafana_url, headers):
    grafana_version = {}
    r, info = fetch_url(
        module, "%s/api/frontend/settings" % grafana_url, headers=headers, method="GET"
    )
    if info["status"] == 200:
        try:
            settings = json.loads(to_text(r.read()))
            grafana_version = parse_grafana_version(settings["buildInfo"]["version"])
        except UnicodeError:
            raise GrafanaAPIException("Unable to decode version string to Unicode")
        except Exception as e:
            raise GrafanaAPIException(e)
    else:
        raise GrafanaAPIException("Unable to get grafana version: %s" % info)

    return grafana_version.get("major")

def grafana_folder_exists(module, grafana_url, folder_name, parent_folder, headers):
    # the 'General' folder is a special case, it's ID is always '0'
    if folder_name == "General":
        return True, 0

    try:
        url = "%s/api/folders" % grafana_url
        if parent_folder:
            url = "%s?parentUid=%s" % (url, parent_folder)

        r, info = fetch_url(module, url, headers=headers, method="GET")

        if info["status"] != 200:
            raise GrafanaAPIException(
                "Unable to query Grafana API for folders (name: %s): %d"
                % (folder_name, info["status"])
            )

        folders = json.loads(r.read())

        for folder in folders:
            if folder_name in (folder["title"], folder["uid"]):
                return True, folder["id"], folder["uid"]
    except Exception as e:
        raise GrafanaAPIException(e)

    return False, 0


def grafana_dashboard_exists(module, grafana_url, uid, headers, api_version="v1", namespace="default"):
    dashboard_exists = False
    dashboard = {}

    grafana_version = get_grafana_version(module, grafana_url, headers)
   
    if grafana_version >= 13:
        uri = "%s/apis/dashboard.grafana.app/%s/namespaces/%s/dashboards/%s" % (grafana_url, api_version, namespace, uid)
    elif grafana_version >= 5:
        uri = "%s/api/dashboards/uid/%s" % (grafana_url, uid)
    else:
        uri = "%s/api/dashboards/db/%s" % (grafana_url, uid)

    r, info = fetch_url(module, uri, headers=headers, method="GET")

    if info["status"] == 200:
        dashboard_exists = True
        try:
            if r.headers["Content-Type"].startswith("application/yaml"):
                dashboard = yaml.safe_load(r.read())
            else:
                dashboard = json.loads(r.read())
                
            if "metadata" in dashboard and "uid" in dashboard["metadata"]:
                del dashboard["metadata"]["uid"]
        except Exception as e:
            raise GrafanaAPIException(e)
    elif info["status"] == 404:
        dashboard_exists = False
    else:
        raise GrafanaAPIException("Unable to get dashboard %s : %s" % (uid, info))

    return dashboard_exists, dashboard


def grafana_dashboard_search(module, grafana_url, folder_id, title, headers, api_version="v1", namespace="default"):
    # search by title
    uri = "%s/api/search?%s" % (
        grafana_url,
        urlencode({"folderIds": folder_id, "query": title, "type": "dash-db"}),
    )
    r, info = fetch_url(module, uri, headers=headers, method="GET")

    if info["status"] == 200:
        try:
            dashboards = json.loads(r.read())
            for d in dashboards:
                if d["title"] == title:
                    return grafana_dashboard_exists(
                        module, grafana_url, d["uid"], headers, api_version=api_version, namespace=namespace
                    )
        except Exception as e:
            raise GrafanaAPIException(e)
    else:
        raise GrafanaAPIException("Unable to search dashboard %s : %s" % (title, info))

    return False, None


# for comparison, we sometimes need to ignore a few keys
def is_grafana_dashboard_changed(payload, dashboard):
    if "apiVersion" in payload and payload["apiVersion"] == "dashboard.grafana.app/v2":
        if "generation" in payload["metadata"]:
            del payload["metadata"]["generation"]
        if "metadata" in dashboard and "generation" in dashboard["metadata"]:
            del dashboard["metadata"]["generation"]

        if "uid" in payload["metadata"]:
            del payload["metadata"]["uid"]
        if "metadata" in dashboard and "uid" in dashboard["metadata"]:
            del dashboard["metadata"]["uid"]

        if "resourceVersion" in payload["metadata"]:
            del payload["metadata"]["resourceVersion"]
        if "metadata" in dashboard and  "resourceVersion" in dashboard["metadata"]:
            del dashboard["metadata"]["resourceVersion"]

        if "creationTimestamp" in payload["metadata"]:
            del payload["metadata"]["creationTimestamp"]
        if "metadata" in dashboard and  "resourceVersion" in dashboard["metadata"]:
            del dashboard["metadata"]["creationTimestamp"]

        if "annotations" in payload["metadata"]:
            del payload["metadata"]["annotations"]
        if "metadata" in dashboard and  "annotations" in dashboard["metadata"]:
            del dashboard["metadata"]["annotations"]


    else:
    # Traditional way
        # you don't need to set the version, but '0' is incremented to '1' by Grafana's API
        if "version" in payload["dashboard"]:
            del payload["dashboard"]["version"]
        if "version" in dashboard["dashboard"]:
            del dashboard["dashboard"]["version"]

        # if folderId is not provided in dashboard,
        # try getting the folderId from the dashboard metadata,
        # otherwise set the default folderId
        if "folderId" not in dashboard:
            dashboard["folderId"] = dashboard["meta"].get("folderId", 0)

        # remove meta key if exists for compare
        if "meta" in dashboard:
            del dashboard["meta"]
        if "meta" in payload:
            del payload["meta"]

        # Ignore dashboard ids since real identifier is uuid
        if "id" in dashboard["dashboard"]:
            del dashboard["dashboard"]["id"]
        if "id" in payload["dashboard"]:
            del payload["dashboard"]["id"]

    if payload == dashboard:
        return False
    return True

def grafana_get_dashboard_details(payload):
    if "apiVersion" in payload and payload["apiVersion"] == "dashboard.grafana.app/v2":
        return "v2", payload.get("spec", {}).get("name"), payload.get("metadata", {}).get("name")
    else:
        return "classic", payload.get("dashboard", {}).get("title"), payload.get("dashboard", {}).get("uid")

def grafana_create_dashboard(module, data):
    # define data payload for grafana API
    payload = {}

    if data.get("dashboard_id"):
        data["path"] = "https://grafana.com/api/dashboards/%s/revisions/%s/download" % (
            data["dashboard_id"],
            data["dashboard_revision"],
        )
    if data["path"].startswith("http"):
        r, info = fetch_url(module, data["path"])
        if info["status"] != 200:
            raise GrafanaAPIException(
                "Unable to download grafana dashboard from url %s : %s"
                % (data["path"], info)
            )
        payload = json.loads(r.read())
    else:
        try:
            with open(data["path"], "r", encoding="utf-8") as in_file:
                if data["path"].endswith(".yaml"):
                    payload = yaml.safe_load(in_file)
                else:
                    payload = json.load(in_file)
        except Exception as e:
            raise GrafanaAPIException("Can't load json file %s" % to_native(e))

    payload_version, payload_title, payload_uid = grafana_get_dashboard_details(payload)

    # Check that the dashboard JSON is nested under the 'dashboard' key
    if payload_version == "classic" and "dashboard" not in payload:
        payload = {"dashboard": payload}

    # define http header
    headers = grafana_headers(module, data)

    grafana_version = get_grafana_version(module, data["url"], headers)

    if grafana_version < 5:
        uid = data.get("slug") or payload.get("meta", {}).get("slug")
        if not uid:
            raise GrafanaMalformedJson("No slug found in JSON. Needed with Grafana < 5")
    else:
        uid = data.get("uid") or payload_uid
        if data.get("uid"):
            if payload_version == "v2":
                payload["metadata"]["name"] = data["uid"]
            else:
                payload["dashboard"]["uid"] = data["uid"]

    result = {}

    # test if the folder exists
    folder_exists = False
    if data["parent_folder"] and grafana_version < 11:
        module.fail_json(
            failed=True, msg="Subfolder API is available starting Grafana v11"
        )

    if grafana_version >= 5:
        folder_exists, folder_id, folder_uid = grafana_folder_exists(
            module, data["url"], data["folder"], data["parent_folder"], headers
        )
        if folder_exists is False:
            raise GrafanaAPIException(
                "Dashboard folder '%s' does not exist." % data["folder"]
            )
        
        if payload_version == "classic":
            payload["folderId"] = folder_id
        else:
            if "annotations" not in payload["metadata"]:
                payload["annotations"] = {}
            payload["metadata"]["annotations"]["grafana.app/folder"] = folder_uid

    # test if dashboard already exists
    if uid:
        dashboard_exists, dashboard = grafana_dashboard_exists(
            module, data["url"], uid, headers=headers, api_version=data["api_version"], namespace=data["namespace"]
        )
    else:
        dashboard_exists, dashboard = grafana_dashboard_search(
            module,
            data["url"],
            folder_id,
            payload_title,
            headers=headers,
            api_version=data["api_version"],
            namespace=data["namespace"],
        )

    # Ensure there is no id in payload
    if payload_version == "classic" and "id" in payload["dashboard"]:
        del payload["dashboard"]["id"]
    if payload_version == "v2" and "uid" in payload["metadata"]:
        del payload["metadata"]["uid"]
    if payload_version == "v2" and "resourceVersion" in payload["metadata"]:
        del payload["metadata"]["resourceVersion"]

    if data["path"].endswith(".yaml"):
        headers["Content-Type"] = "application/yaml; charset=utf8"
        payload_formatted = yaml.dump(payload, default_flow_style=False)
    else:
        payload_formatted = json.dumps(payload)

    if dashboard_exists is True:
        grafana_dashboard_changed = is_grafana_dashboard_changed(payload, dashboard)

        if grafana_dashboard_changed:
            if module.check_mode:
                module.exit_json(
                    uid=uid,
                    failed=False,
                    changed=True,
                    msg="Dashboard %s will be updated" % payload_title,
                )
            # update
            if "overwrite" in data and data["overwrite"]:
                payload["overwrite"] = True
            if "commit_message" in data and data["commit_message"]:
                payload["message"] = data["commit_message"]

            if grafana_version >= 13:
                r, info = fetch_url(
                    module,
                    "%s/apis/dashboard.grafana.app/%s/namespaces/%s/dashboards/%s" % (data["url"], data['api_version'], data["namespace"], uid),
                    data=payload_formatted,
                    headers=headers,
                    method="PUT",
                )
            else:
                r, info = fetch_url(
                    module,
                    "%s/api/dashboards/db" % data["url"],
                    data=json.dumps(payload),
                    headers=headers,
                    method="POST",
                )
            if info["status"] == 200:
                if grafana_version >= 5:
                    try:
                        dashboard = json.loads(r.read())
                        if "metadata" in dashboard and "name" in dashboard["metadata"]:
                            uid = dashboard["metadata"]["name"]
                        elif "uid" in dashboard:
                            uid = dashboard["uid"]
                    except Exception as e:
                        raise GrafanaAPIException(e)
                result["uid"] = uid
                result["msg"] = "Dashboard %s updated" % payload_title
                result["changed"] = True
            else:
                body = json.loads(info["body"])
                raise GrafanaAPIException(
                    "Unable to update the dashboard %s : %s (HTTP: %d)"
                    % (uid, body["message"], info["status"])
                )
        else:
            # unchanged
            result["uid"] = uid
            result["msg"] = "Dashboard %s unchanged." % payload_title
            result["changed"] = False
    else:
        if module.check_mode:
            module.exit_json(
                failed=False,
                changed=True,
                msg="Dashboard %s will be created" % payload_title,
            )

        if grafana_version >= 13:
            r, info = fetch_url(
                module,
                "%s/apis/dashboard.grafana.app/%s/namespaces/%s/dashboards/%s" % (data["url"], data["api_version"], data["namespace"], uid),
                data=payload_formatted,
                headers=headers,
                method="PUT",
            )
        else:
            r, info = fetch_url(
                module,
                "%s/api/dashboards/db" % data["url"],
                data=json.dumps(payload),
                headers=headers,
                method="POST",
            )
        if info["status"] == 200 or info["status"] == 201:
            result["msg"] = "Dashboard %s created" % payload_title
            result["changed"] = True
            if grafana_version >= 5:
                try:
                    dashboard_version, dashboard_title, dashboard_uid = grafana_get_dashboard_details(json.loads(r.read()))
                    uid = dashboard_uid
                except Exception as e:
                    raise GrafanaAPIException(e)
            result["uid"] = uid
        else:
            raise GrafanaAPIException(
                "Unable to create the new dashboard %s : %s - %s. (headers : %s)"
                % (payload_title, info["status"], info, headers)
            )

    return result


def grafana_delete_dashboard(module, data):
    # define http headers
    headers = grafana_headers(module, data)

    grafana_version = get_grafana_version(module, data["url"], headers)
    if grafana_version < 5:
        if data.get("slug"):
            uid = data["slug"]
        else:
            raise GrafanaMalformedJson("No slug parameter. Needed with grafana < 5")
    else:
        if data.get("uid"):
            uid = data["uid"]
        else:
            raise GrafanaDeleteException("No uid specified %s")

    # test if dashboard already exists
    dashboard_exists, dashboard = grafana_dashboard_exists(
        module, data["url"], uid, headers=headers
    )

    result = {}
    if dashboard_exists is True:
        if module.check_mode:
            module.exit_json(
                uid=uid,
                failed=False,
                changed=True,
                msg="Dashboard %s will be deleted" % uid,
            )

        # delete
        if grafana_version < 5:
            r, info = fetch_url(
                module,
                "%s/api/dashboards/db/%s" % (data["url"], uid),
                headers=headers,
                method="DELETE",
            )
        else:
            r, info = fetch_url(
                module,
                "%s/api/dashboards/uid/%s" % (data["url"], uid),
                headers=headers,
                method="DELETE",
            )
        if info["status"] == 200:
            result["msg"] = "Dashboard %s deleted" % uid
            result["changed"] = True
            result["uid"] = uid
        else:
            raise GrafanaAPIException(
                "Unable to update the dashboard %s : %s" % (uid, info)
            )
    else:
        # dashboard does not exist, do nothing
        result = {
            "msg": "Dashboard %s does not exist." % uid,
            "changed": False,
            "uid": uid,
        }

    return result


def grafana_export_dashboard(module, data):
    # define http headers
    headers = grafana_headers(module, data)

    grafana_version = get_grafana_version(module, data["url"], headers)
    if grafana_version < 5:
        if data.get("slug"):
            uid = data["slug"]
        else:
            raise GrafanaMalformedJson("No slug parameter. Needed with grafana < 5")
    else:
        if data.get("uid"):
            uid = data["uid"]
        else:
            raise GrafanaExportException("No uid specified")

    if data["path"].endswith(".yaml") is True:
        headers["Accept"] = "application/yaml"


    # test if dashboard already exists
    dashboard_exists, dashboard = grafana_dashboard_exists(
        module, data["url"], uid, headers=headers, api_version=data["api_version"], namespace=data["namespace"]
    )

    if dashboard_exists is True:
        if module.check_mode:
            module.exit_json(
                uid=uid,
                failed=False,
                changed=True,
                msg="Dashboard %s will be exported to %s" % (uid, data["path"]),
            )
        try:
            with open(data["path"], "w", encoding="utf-8") as f:
                if data["path"].endswith(".yaml"):
                    f.write(yaml.dump(dashboard, default_flow_style=False))
                else:
                    f.write(json.dumps(dashboard, indent=2))
        except Exception as e:
            raise GrafanaExportException("Can't write json file : %s" % to_native(e))
        result = {
            "msg": "Dashboard %s exported to %s" % (uid, data["path"]),
            "uid": uid,
            "changed": True,
        }
    else:
        result = {
            "msg": "Dashboard %s does not exist." % uid,
            "uid": uid,
            "changed": False,
        }

    return result


def main():
    # use the predefined argument spec for url
    argument_spec = grafana_argument_spec()
    argument_spec.update(
        state=dict(choices=["present", "absent", "export"], default="present"),
        org_id=dict(default=1, type="int"),
        org_name=dict(type="str"),
        folder=dict(type="str", default="General"),
        parent_folder=dict(type="str"),
        uid=dict(type="str"),
        slug=dict(type="str"),
        path=dict(aliases=["dashboard_url"], type="str"),
        dashboard_id=dict(type="str"),
        dashboard_revision=dict(type="str", default="1"),
        overwrite=dict(type="bool", default=False),
        commit_message=dict(type="str"),
        api_version=dict(type="str", choices=["v1", "v2"], default="v1"),
        namespace=dict(type="str", default="default"),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["state", "export", ["path"]],
        ],
        required_together=[["url_username", "url_password", "org_id"]],
        mutually_exclusive=[
            ["url_username", "grafana_api_key"],
            ["uid", "slug"],
            ["path", "dashboard_id"],
            ["org_id", "org_name"],
        ],
    )

    module.params["url"] = clean_url(module.params["url"])

    try:
        if module.params["state"] == "present":
            result = grafana_create_dashboard(module, module.params)
        elif module.params["state"] == "absent":
            result = grafana_delete_dashboard(module, module.params)
        else:
            result = grafana_export_dashboard(module, module.params)
    except GrafanaAPIException as e:
        module.fail_json(failed=True, msg="error : %s" % to_native(e))
        return
    except GrafanaMalformedJson as e:
        module.fail_json(failed=True, msg="error : %s" % to_native(e))
        return
    except GrafanaDeleteException as e:
        module.fail_json(
            failed=True, msg="error : Can't delete dashboard : %s" % to_native(e)
        )
        return
    except GrafanaExportException as e:
        module.fail_json(
            failed=True, msg="error : Can't export dashboard : %s" % to_native(e)
        )
        return

    module.exit_json(failed=False, **result)
    return


if __name__ == "__main__":
    main()
