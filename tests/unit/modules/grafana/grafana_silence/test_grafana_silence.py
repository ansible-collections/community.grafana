from __future__ import absolute_import, division, print_function

from unittest import TestCase
from unittest.mock import patch
from ansible_collections.community.grafana.plugins.modules import grafana_silence
from ansible.module_utils._text import to_bytes
from ansible.module_utils import basic
from ansible.module_utils.urls import basic_auth_header
import json

__metaclass__ = type


class MockedReponse(object):
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""

    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""

    pass


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)


def silence_deleted_resp():
    server_response = json.dumps({"message": "silence deleted"})
    return (MockedReponse(server_response), {"status": 200})


def silence_created_resp():
    server_response = json.dumps({"silenceID": "470b7116-8f06-4bb6-9e6c-6258aa92218e"})
    return (MockedReponse(server_response), {"status": 200})


def silence_get_resp():
    server_response = json.dumps([], sort_keys=True)
    return (MockedReponse(server_response), {"status": 200})


def get_silence_by_id_resp():
    server_response = json.dumps([], sort_keys=True)
    return (MockedReponse(server_response), {"status": 200})


def get_version_resp():
    return {"major": 10, "minor": 0, "rev": 0}


class GrafanaSilenceTest(TestCase):
    def setUp(self):
        self.authorization = basic_auth_header("admin", "changeme")
        self.mock_module_helper = patch.multiple(
            basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json
        )
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    # create a new silence
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_silence.GrafanaSilenceInterface.get_silence"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_silence.GrafanaSilenceInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_silence.fetch_url"
    )
    def test_create_silence_new_silence(
        self, mock_fetch_url, mock_get_version, mock_get_silence
    ):
        set_module_args(
            {
                "url": "https://grafana.example.com",
                "url_username": "admin",
                "url_password": "changeme",
                "comment": "a testcomment",
                "created_by": "me",
                "starts_at": "2029-07-29T08:45:45.000Z",
                "ends_at": "2029-07-29T08:55:45.000Z",
                "matchers": [
                    {
                        "isEqual": True,
                        "isRegex": True,
                        "name": "environment",
                        "value": "test",
                    }
                ],
                "state": "present",
            }
        )
        module = grafana_silence.setup_module_object()
        mock_get_version.return_value = get_version_resp()
        mock_fetch_url.return_value = silence_created_resp()
        mock_get_silence.return_value = silence_get_resp()

        grafana_iface = grafana_silence.GrafanaSilenceInterface(module)
        result = grafana_iface.create_silence(
            "a testcomment",
            "me",
            "2029-07-29T08:45:45.000Z",
            "2029-07-29T08:55:45.000Z",
            [
                {
                    "isEqual": True,
                    "isRegex": True,
                    "name": "environment",
                    "value": "test",
                }
            ],
        )
        mock_fetch_url.assert_called_once_with(
            module,
            "https://grafana.example.com/api/alertmanager/grafana/api/v2/silences",
            data=json.dumps(
                {
                    "comment": "a testcomment",
                    "createdBy": "me",
                    "startsAt": "2029-07-29T08:45:45.000Z",
                    "endsAt": "2029-07-29T08:55:45.000Z",
                    "matchers": [
                        {
                            "isEqual": True,
                            "isRegex": True,
                            "name": "environment",
                            "value": "test",
                        }
                    ],
                },
                sort_keys=True,
            ),
            headers={
                "Content-Type": "application/json",
                "Authorization": self.authorization,
            },
            method="POST",
        )
        self.assertEquals(result, {"silenceID": "470b7116-8f06-4bb6-9e6c-6258aa92218e"})

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_silence.GrafanaSilenceInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_silence.fetch_url"
    )
    def test_delete_silence(self, mock_fetch_url, mock_get_version):
        set_module_args(
            {
                "url": "https://grafana.example.com",
                "url_username": "admin",
                "url_password": "changeme",
                "comment": "a testcomment",
                "created_by": "me",
                "ends_at": "2029-07-29T08:55:45.000Z",
                "matchers": [
                    {
                        "isEqual": True,
                        "isRegex": True,
                        "name": "environment",
                        "value": "test",
                    }
                ],
                "starts_at": "2029-07-29T08:45:45.000Z",
                "state": "present",
            }
        )
        module = grafana_silence.setup_module_object()
        mock_fetch_url.return_value = silence_deleted_resp()
        mock_get_version.return_value = get_version_resp()

        grafana_iface = grafana_silence.GrafanaSilenceInterface(module)
        silence_id = "470b7116-8f06-4bb6-9e6c-6258aa92218e"
        result = grafana_iface.delete_silence(silence_id)
        mock_fetch_url.assert_called_once_with(
            module,
            "https://grafana.example.com/api/alertmanager/grafana/api/v2/silence/470b7116-8f06-4bb6-9e6c-6258aa92218e",
            data=None,
            headers={
                "Content-Type": "application/json",
                "Authorization": self.authorization,
            },
            method="DELETE",
        )
        self.assertEquals(result, {"message": "silence deleted"})
