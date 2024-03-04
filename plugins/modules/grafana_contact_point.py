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

__metaclass__ = type

DOCUMENTATION = """
---
module: grafana_contact_point
author:
  - Moritz Pötschk (@nemental)
version_added: "1.9.0"
short_description: Manage Grafana Contact Points
description:
  - Create/Update/Delete Grafana Contact Points via API.

extends_documentation_fragment:
  - community.grafana.basic_auth
  - community.grafana.api_key
"""


EXAMPLES = """
- name: Create email contact point
  community.grafana.grafana_contact_point:
    grafana_url: "{{ grafana_url }}"
    grafana_user: "{{ grafana_username }}"
    grafana_password: "{{ grafana_password }}"
    uid: email
    name: E-Mail
    type: email
    email_addresses:
      - example@example.com

- name: Delete email contact point
  community.grafana.grafana_contact_point:
    grafana_url: "{{ grafana_url }}"
    grafana_user: "{{ grafana_username }}"
    grafana_password: "{{ grafana_password }}"
    uid: email
    state: absent
"""

RETURN = """
contact_point:
  description: Contact point created or updated by the module.
  returned: changed
"""

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text
from ansible_collections.community.grafana.plugins.module_utils.base import (
    grafana_argument_spec,
    clean_url,
)
from ansible.module_utils.urls import basic_auth_header


class GrafanaAPIException(Exception):
    pass


def grafana_contact_point_payload(data):
    payload = {
        "uid": data["uid"],
        "name": data["name"],
        "type": data["type"],
        "isDefault": data["is_default"],
        "disableResolveMessage": data["disable_resolve_message"],
    }

    return payload


def grafana_contact_point_payload_email(data, payload):
    payload["settings"]["addresses"] = ";".join(data["email_addresses"])
    if data.get("email_single"):
        payload["settings"]["singleEmail"] = data["email_single"]


def grafana_contact_point_payload(data):
    payload = {
        "uid": data["uid"],
        "name": data["name"],
        "type": data["type"],
        "isDefault": data["is_default"],
        "disableResolveMessage": data["disable_resolve_message"],
        "settings": {"uploadImage": data["include_image"]},
    }

    if data["type"] == "email":
        grafana_contact_point_payload_email(data, payload)

    return payload


class GrafanaContactPointInterface(object):
    def __init__(self, module):
        self._module = module
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
                self.grafana_organization_by_name(module.params["org_name"])
                if module.params["org_name"]
                else module.params["org_id"]
            )
            self.grafana_switch_organisation(module.params, self.org_id)
        # }}}

    def grafana_organization_by_name(self, data, org_name):
        r, info = fetch_url(
            self._module,
            "%s/api/user/orgs" % data["url"],
            headers=self.headers,
            method="GET",
        )
        organizations = json.loads(to_text(r.read()))
        orga = next((org for org in organizations if org["name"] == org_name))
        if orga:
            return orga["orgId"]

        raise GrafanaAPIException(
            "Current user isn't member of organization: %s" % org_name
        )

    def grafana_switch_organisation(self, data, org_id):
        r, info = fetch_url(
            self._module,
            "%s/api/user/using/%s" % (data["url"], org_id),
            headers=self.headers,
            method="POST",
        )
        if info["status"] != 200:
            raise GrafanaAPIException(
                "Unable to switch to organization %s : %s" % (org_id, info)
            )

    def grafana_check_contact_point_match(self, data):
        r, info = fetch_url(
            self._module,
            "%s/api/v1/provisioning/contact-points" % data["url"],
            headers=self.headers,
            method="GET",
        )

        if info["status"] == 200:
            contact_points = json.loads(to_text(r.read()))
            before = next(
                (cp for cp in contact_points if cp["uid"] == data["uid"]), None
            )
            return self.grafana_handle_contact_point(data, before)
        else:
            raise GrafanaAPIException(
                "Unable to get contact point %s : %s" % (data["uid"], info)
            )

    def grafana_handle_contact_point(self, data, before):
        payload = grafana_contact_point_payload(data)

        if data["state"] == "present":
            if before:
                return self.grafana_update_contact_point(data, payload, before)
            else:
                return self.grafana_create_contact_point(data, payload)
        else:
            if before:
                return self.grafana_delete_contact_point(data)
            else:
                return {"changed": False}

    def grafana_create_contact_point(self, data, payload):
        r, info = fetch_url(
            self._module,
            "%s/api/v1/provisioning/contact-points" % data["url"],
            data=json.dumps(payload),
            headers=self.headers,
            method="POST",
        )

        if info["status"] == 202:
            contact_point = json.loads(to_text(r.read()))
            return {
                "changed": True,
                "state": data["state"],
                "contact_point": contact_point,
            }
        else:
            raise GrafanaAPIException("Unable to create contact point: %s" % info)

    def grafana_update_contact_point(self, data, payload, before):
        r, info = fetch_url(
            self._module,
            "%s/api/v1/provisioning/contact-points/%s" % (data["url"], data["uid"]),
            data=json.dumps(payload),
            headers=self.headers,
            method="PUT",
        )

        if info["status"] == 202:
            contact_point = json.loads(to_text(r.read()))

            if before == contact_point:
                return {"changed": False}
            else:
                return {
                    "changed": True,
                    "diff": {"before": before, "after": payload},
                    "contact_point": contact_point,
                }
        else:
            raise GrafanaAPIException(
                "Unable to update contact point %s : %s" % (data["uid"], info)
            )

    def grafana_delete_contact_point(self, data):
        r, info = fetch_url(
            self._module,
            "%s/api/v1/provisioning/contact-points/%s" % (data["url"], data["uid"]),
            headers=self.headers,
            method="DELETE",
        )

        if info["status"] == 202:
            return {"state": "absent", "changed": True}
        elif info["status"] == 404:
            return {"changed": False}
        else:
            raise GrafanaAPIException(
                "Unable to delete contact point %s : %s" % (data["uid"], info)
            )


def main():
    argument_spec = grafana_argument_spec()
    argument_spec.update(
        # general arguments
        disable_resolve_message=dict(type="bool", default=False),
        include_image=dict(type="bool", default=False),
        is_default=dict(type="bool", default=False),
        name=dict(type="str"),
        org_id=dict(type="int", default=1),
        org_name=dict(type="str"),
        type=dict(
            type="str",
            choices=[
                "alertmanager",
                "dingding",
                "discord",
                "email",
                "googlechat",
                "kaska",
                "line",
                "opsgenie",
                "pagerduty",
                "pushover",
                "sensugo",
                "slack",
                "teams",
                "telegram",
                "threema",
                "victorops",
                "webex",
                "webhook",
                "wecom",
            ],
        ),
        uid=dict(type="str"),
        # type: alertmanager
        alertmanager_password=dict(type="str", no_log=True),
        alertmanager_url=dict(type="str"),
        alertmanager_username=dict(type="str"),
        # type: dingding
        dingding_message=dict(type="str"),
        dingding_message_type=dict(type="str"),
        dingding_title=dict(type="str"),
        dingding_url=dict(type="str"),
        # type: discord
        discord_avatar_url=dict(type="str"),
        discord_message=dict(type="str"),
        discord_title=dict(type="str"),
        discord_url=dict(type="str", no_log=True),
        discord_use_username=dict(type="bool", default=False),
        # type: email
        email_addresses=dict(type="list", elements="str"),
        email_message=dict(type="str"),
        email_single=dict(type="bool", default=False),
        email_subject=dict(type="str"),
        # type: googlechat
        googlechat_url=dict(type="str", no_log=True),
        googlechat_message=dict(type="str"),
        googlechat_title=dict(type="str"),
        # type: kafka
        kafka_api_version=dict(type="str", default="v2"),
        kafka_cluster_id=dict(type="str"),
        kafka_description=dict(type="str"),
        kafka_details=dict(type="str"),
        kafka_password=dict(type="str", no_log=True),
        kafka_rest_proxy_url=dict(type="str", no_log=True),
        kafka_topic=dict(type="str"),
        kafka_username=dict(type="str"),
        # type: line
        line_description=dict(type="str"),
        line_title=dict(type="str"),
        line_token=dict(type="str", no_log=True),
        # type: opsgenie
        opsgenie_api_key=dict(type="str", no_log=True),
        opsgenie_auto_close=dict(type="bool"),
        opsgenie_description=dict(type="str"),
        opsgenie_message=dict(type="str"),
        opsgenie_override_priority=dict(type="bool"),
        opsgenie_responders=dict(type="list", elements="dict"),
        opsgenie_send_tags_as=dict(type="str"),
        opsgenie_url=dict(type="str"),
        # type: pagerduty
        pagerduty_class=dict(type="str"),
        pagerduty_client=dict(type="str"),
        pagerduty_client_url=dict(type="str"),
        pagerduty_component=dict(type="str"),
        pagerduty_details=dict(type="list", elements="dict"),
        pagerduty_group=dict(type="str"),
        pagerduty_integration_key=dict(type="str", no_log=True),
        pagerduty_severity=dict(
            type="str", choices=["critical", "error", "warning", "info"]
        ),
        pagerduty_source=dict(type="str"),
        pagerduty_summary=dict(type="str"),
        # type: pushover
        pushover_api_token=dict(type="str", no_log=True),
        pushover_devices=dict(type="list", elements="str"),
        pushover_expire=dict(type="int"),
        pushover_message=dict(type="str"),
        pushover_ok_priority=dict(type="int"),
        pushover_ok_sound=dict(type="str"),
        pushover_priority=dict(type="int"),
        pushover_retry=dict(type="int"),
        pushover_sound=dict(type="str"),
        pushover_title=dict(type="str"),
        pushover_upload_image=dict(type="bool", default=True),
        pushover_user_key=dict(type="str", no_log=True),
        # type: sensugo
        sensugo_api_key=dict(type="str", no_log=True),
        sensugo_url=dict(type="str"),
        sensugo_check=dict(type="str"),
        sensugo_entity=dict(type="str"),
        sensugo_handler=dict(type="str"),
        sensugo_message=dict(type="str"),
        sensugo_namespace=dict(type="str"),
        # type: slack
        slack_endpoint_url=dict(type="str"),
        slack_icon_emoji=dict(type="str"),
        slack_icon_url=dict(type="str"),
        slack_mention_channel=dict(type="str", choices=["here", "channel"]),
        slack_mention_groups=dict(type="list"),
        slack_mention_users=dict(type="list"),
        slack_recipient=dict(type="str"),
        slack_text=dict(type="str"),
        slack_title=dict(type="str"),
        slack_token=dict(type="str", no_log=True),
        slack_url=dict(type="str", no_log=True),
        slack_username=dict(type="str"),
        # type: teams
        teams_message=dict(type="str"),
        teams_section_title=dict(type="str"),
        teams_title=dict(type="str"),
        teams_url=dict(type="str", no_log=True),
        # type: telegram
        telegram_chat_id=dict(type="str"),
        telegram_disable_notifications=dict(type="bool"),
        telegram_message=dict(type="str"),
        telegram_parse_mode=dict(type="str"),
        telegram_protect_content=dict(type="bool"),
        telegram_token=dict(type="str", no_log=True),
        telegram_web_page_view=dict(type="bool"),
        # type: threema
        threema_api_secret=dict(type="str", no_log=True),
        threema_description=dict(type="str"),
        threema_gateway_id=dict(type="str"),
        threema_recipient_id=dict(type="str"),
        threema_title=dict(type="str"),
        # type: victorops
        victorops_description=dict(type="str"),
        victorops_message_type=dict(type="str", choices=["CRITICAL", "RECOVERY"]),
        victorops_title=dict(type="str"),
        victorops_url=dict(type="str"),
        # type: webex
        webex_api_url=dict(type="str"),
        webex_message=dict(type="str"),
        webex_room_id=dict(type="str"),
        webex_token=dict(type="str", no_log=True),
        # type: webhook
        webhook_authorization_credentials=dict(type="str", no_log=True),
        webhook_authorization_scheme=dict(type="str"),
        webhook_http_method=dict(type="str", choices=["POST", "PUT"]),
        webhook_max_alerts=dict(type="int"),
        webhook_message=dict(type="str"),
        webhook_password=dict(type="str", no_log=True),
        webhook_title=dict(type="str"),
        webhook_url=dict(type="str"),
        webhook_username=dict(type="str"),
        # type: wecom
        wecom_agent_id=dict(type="str"),
        wecom_corp_id=dict(type="str"),
        wecom_message=dict(type="str"),
        wecom_msg_type=dict(type="str"),
        wecom_secret=dict(type="str", no_log=True),
        wecom_title=dict(type="str"),
        wecom_to_user=dict(type="list"),
        wecom_url=dict(type="str", no_log=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[["url_username", "url_password", "org_id"]],
        mutually_exclusive=[["url_username", "grafana_api_key"]],
        required_if=[
            ["state", "present", ["name", "type"]],
            ["state", "absent", ["uid"]],
            ["type", "alertmanager", ["alertmanager_url"]],
            ["type", "dingding", ["dingding_url"]],
            ["type", "discord", ["discord_url"]],
            ["type", "email", ["email_addresses"]],
            ["type", "googlechat", ["googlechat_url"]],
            ["type", "kafka", ["kafka_rest_proxy_url", "kafka_topic"]],
            ["type", "line", ["line_token"]],
            ["type", "opsgenie", ["opsgenie_api_key"]],
            ["type", "pagerduty", ["pagerduty_integration_key"]],
            ["type", "pushover", ["pushover_api_token", "pushover_user_key"]],
            ["type", "sensugo", ["sensugo_api_key", "sensugo_url"]],
            ["type", "slack", ["slack_recipient", "slack_token", "slack_url"]],
            ["type", "teams", ["teams_url"]],
            ["type", "telegram", ["telegram_chat_id", "telegram_token"]],
            [
                "type",
                "threema",
                ["threema_api_secret", "threema_gateway_id", "threema_recipient_id"],
            ],
            ["type", "victorops", ["victorops_url"]],
            ["type", "webex", ["webex_token", "webex_room_id"]],
            ["type", "webhook", ["webhook_url"]],
            [
                "type",
                "wecom",
                ["wecom_url", "wecom_agent_id", "wecom_corp_id", "wecom_secret"],
            ],
        ],
    )

    module.params["url"] = clean_url(module.params["url"])
    grafana_iface = GrafanaContactPointInterface(module)

    result = grafana_iface.grafana_check_contact_point_match(module.params)
    module.exit_json(failed=False, **result)


if __name__ == "__main__":
    main()
