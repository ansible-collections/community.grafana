from __future__ import absolute_import, division, print_function

import json
from unittest.mock import MagicMock, patch

from ansible_collections.community.grafana.plugins.modules import grafana_contact_point

__metaclass__ = type


class MockedReponse(object):
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data


CONTACT_POINT = {
    "uid": "email",
    "name": "E-Mail",
    "type": "email",
    "settings": {"addresses": "sre@example.org"},
    "disableResolveMessage": False,
    "provenance": "api",
}

DATA = {
    "url": "https://grafana.example.com",
    "uid": "email",
    "provisioning": True,
    "state": "present",
}


def update(current, after):
    iface = grafana_contact_point.GrafanaContactPointInterface.__new__(
        grafana_contact_point.GrafanaContactPointInterface
    )
    iface._module = MagicMock()
    iface.headers = {"Content-Type": "application/json"}
    iface.contact_point = current
    responses = [
        (MockedReponse(""), {"status": 202}),
        (MockedReponse(json.dumps([after])), {"status": 200}),
    ]
    with patch.object(grafana_contact_point, "fetch_url", side_effect=responses):
        return iface.grafana_update_contact_point(DATA, {})


def test_update_unchanged_with_provenance():
    result = update(dict(CONTACT_POINT), dict(CONTACT_POINT))

    assert result["changed"] is False


def test_update_changed_with_provenance():
    after = dict(CONTACT_POINT, settings={"addresses": "new@example.org"})

    result = update(dict(CONTACT_POINT), after)

    assert result["changed"] is True
    assert result["diff"]["before"] == CONTACT_POINT
