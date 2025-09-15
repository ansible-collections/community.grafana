from __future__ import absolute_import, division, print_function

from unittest import TestCase
from unittest.mock import patch
from ansible_collections.community.grafana.plugins.modules import grafana_team
from ansible.module_utils import basic
from ansible.module_utils.urls import basic_auth_header
from contextlib import contextmanager
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


@contextmanager
def set_module_args(args):
    """Context manager that sets module arguments for AnsibleModule"""

    try:
        from ansible.module_utils.testing import patch_module_args
    except ImportError:
        from ansible.module_utils._text import to_bytes

        serialized_args = to_bytes(json.dumps({"ANSIBLE_MODULE_ARGS": args}))
        with patch.object(basic, "_ANSIBLE_ARGS", serialized_args):
            yield
    else:
        with patch_module_args(args):
            yield


def lookup_org_resp():
    server_response = json.dumps(
        [
            {"orgId": 1, "name": "Main Org.", "role": "Admin"},
        ]
    )
    return (MockedReponse(server_response), {"status": 200})


def cant_switch_org_resp():
    return (None, {"status": 500})


def switch_org_resp():
    return (None, {"status": 200})


def unauthorized_resp(module, full_url, **kwargs):
    if "/api/user/using/" in full_url:
        # switch organization succeeds
        return (None, {"status": 200})
    return (None, {"status": 401})


def permission_denied_resp(module, full_url, **kwargs):
    if "/api/user/using/" in full_url:
        # switch organization succeeds
        return (None, {"status": 200})
    return (None, {"status": 403})


def get_version_resp():
    return {"major": 6, "minor": 0, "rev": 0}


def get_low_version_resp():
    return {"major": 4, "minor": 6, "rev": 0}


def team_exists_resp():
    server_response = json.dumps(
        {"totalCount": 1, "teams": [{"name": "MyTestTeam", "email": "email@test.com"}]},
        sort_keys=True,
    )
    return (MockedReponse(server_response), {"status": 200})


def team_not_found_resp():
    server_response = json.dumps({"totalCount": 0, "teams": []})
    return (MockedReponse(server_response), {"status": 200})


def team_created_resp():
    server_response = json.dumps({"message": "Team created", "teamId": 2})
    return (MockedReponse(server_response), {"status": 200})


def team_updated_resp():
    server_response = json.dumps({"message": "Team updated"})
    return (MockedReponse(server_response), {"status": 200})


def team_deleted_resp():
    server_response = json.dumps({"message": "Team deleted"})
    return (MockedReponse(server_response), {"status": 200})


def team_members_resp():
    server_response = json.dumps(
        [
            {
                "orgId": 1,
                "teamId": 2,
                "userId": 3,
                "email": "user1@email.com",
                "login": "user1",
                "avatarUrl": r"\/avatar\/1b3c32f6386b0185c40d359cdc733a79",
            },
            {
                "orgId": 1,
                "teamId": 2,
                "userId": 2,
                "email": "user2@email.com",
                "login": "user2",
                "avatarUrl": r"\/avatar\/cad3c68da76e45d10269e8ef02f8e73e",
            },
        ]
    )
    return (MockedReponse(server_response), {"status": 200})


def team_members_no_members_resp():
    server_response = json.dumps([])
    return (MockedReponse(server_response), {"status": 200})


def add_team_member_resp():
    server_response = json.dumps({"message": "Member added to Team"})
    return (MockedReponse(server_response), {"status": 200})


def delete_team_member_resp():
    server_response = json.dumps({"message": "Team Member removed"})
    return (MockedReponse(server_response), {"status": 200})


class GrafanaTeamsTest(TestCase):
    def setUp(self):
        self.authorization = basic_auth_header("admin", "admin")
        self.mock_module_helper = patch.multiple(
            basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json
        )

        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_module_setup_fails_without_params(self):
        with set_module_args({}):
            with self.assertRaises(AnsibleFailJson) as result:
                grafana_team.main()
                err, arg_list = result.exception.args[0]["msg"].split(":")
                self.assertEqual(err, "missing required arguments")
                self.assertEqual(arg_list, ["name", "email", "url"])

    def test_module_setup_fails_without_name(self):
        with set_module_args(
            {"email": "email@test.com", "url": "http://grafana.example.com"}
        ):
            with self.assertRaises(AnsibleFailJson) as result:
                grafana_team.main()
            self.assertEqual(
                result.exception.args[0]["msg"], "missing required arguments: name"
            )

    def test_module_setup_fails_without_email(self):
        with set_module_args(
            {"name": "MyTestTeam", "url": "http://grafana.example.com"}
        ):
            with self.assertRaises(AnsibleFailJson) as result:
                grafana_team.main()
            self.assertEqual(
                result.exception.args[0]["msg"], "missing required arguments: email"
            )

    def test_module_setup_fails_without_url(self):
        with set_module_args(
            {
                "name": "MyTestTeam",
                "email": "email@test.com",
            }
        ):
            with self.assertRaises(AnsibleFailJson) as result:
                grafana_team.main()
            self.assertEqual(
                result.exception.args[0]["msg"], "missing required arguments: url"
            )

    def test_module_setup_fails_with_mutually_exclusive_auth_methods(self):
        with set_module_args(
            {
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
                "grafana_user": "admin",
                "grafana_api_key": "random_api_key",
            }
        ):
            with self.assertRaises(AnsibleFailJson) as result:
                grafana_team.main()
            self.assertEqual(
                result.exception.args[0]["msg"],
                "parameters are mutually exclusive: url_username|grafana_api_key",
            )

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_module_fails_with_low_grafana_version(
        self, mock_fetch_url, mock_get_version
    ):
        with set_module_args(
            {
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
                "grafana_user": "admin",
                "grafana_password": "admin",
            }
        ):
            mock_fetch_url.return_value = switch_org_resp()
            mock_get_version.return_value = get_low_version_resp()

            with self.assertRaises(AnsibleFailJson) as result:
                grafana_team.main()
            self.assertEqual(
                result.exception.args[0]["msg"],
                "Teams API is available starting Grafana v5",
            )

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_module_failure_with_unauthorized_resp(
        self, mock_fetch_url, mock_get_version
    ):
        with set_module_args(
            {
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
            }
        ):
            mock_fetch_url.side_effect = unauthorized_resp
            mock_get_version.return_value = get_version_resp()

            with self.assertRaises(AnsibleFailJson) as result:
                grafana_team.main()
            self.assertTrue(
                result.exception.args[0]["msg"].startswith(
                    "Unauthorized to perform action"
                )
            )

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_module_failure_with_permission_denied_resp(
        self, mock_fetch_url, mock_get_version
    ):
        with set_module_args(
            {
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
            }
        ):
            mock_fetch_url.side_effect = permission_denied_resp
            mock_get_version.return_value = get_version_resp()

            with self.assertRaises(AnsibleFailJson) as result:
                grafana_team.main()
            self.assertTrue(
                result.exception.args[0]["msg"].startswith("Permission Denied")
            )

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_lookup_org_resp(self, mock_fetch_url, mock_get_version):
        with set_module_args(
            {
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
            }
        ):
            module = grafana_team.setup_module_object()
            mock_fetch_url.return_value = lookup_org_resp()
            mock_get_version.return_value = get_version_resp()

            grafana_iface = grafana_team.GrafanaTeamInterface(module)
            res = grafana_iface.organization_by_name("Main Org.")
            mock_fetch_url.assert_called_with(
                module,
                "http://grafana.example.com/api/user/orgs",
                data=None,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": self.authorization,
                },
                method="GET",
            )
            self.assertEqual(res, 1)

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_module_failure_with_lookup_org_resp(
        self, mock_fetch_url, mock_get_version
    ):
        with set_module_args(
            {
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
                "org_name": "Other Org.",
            }
        ):
            mock_fetch_url.return_value = lookup_org_resp()
            mock_get_version.return_value = get_version_resp()

            with self.assertRaises(AnsibleFailJson) as result:
                grafana_team.main()
            self.assertTrue(
                result.exception.args[0]["msg"].startswith(
                    "Current user isn't member of organization: Other Org."
                )
            )

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_module_failure_with_cant_switch_org_resp(
        self, mock_fetch_url, mock_get_version
    ):
        with set_module_args(
            {
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
            }
        ):
            mock_fetch_url.return_value = cant_switch_org_resp()
            mock_get_version.return_value = get_version_resp()

            with self.assertRaises(AnsibleFailJson) as result:
                grafana_team.main()
            self.assertTrue(
                result.exception.args[0]["msg"].startswith(
                    "Unable to switch to organization"
                )
            )

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_get_team_method_with_existing_team(self, mock_fetch_url, mock_get_version):
        with set_module_args(
            {
                "state": "present",
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
            }
        ):
            module = grafana_team.setup_module_object()
            mock_fetch_url.return_value = team_exists_resp()
            mock_get_version.return_value = get_version_resp()

            grafana_iface = grafana_team.GrafanaTeamInterface(module)
            res = grafana_iface.get_team("MyTestTeam")
            self.assertEqual(mock_fetch_url.call_count, 2)
            mock_fetch_url.assert_called_with(
                module,
                "http://grafana.example.com/api/teams/search?name=MyTestTeam",
                data=None,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": self.authorization,
                },
                method="GET",
            )
            self.assertEqual(res, {"email": "email@test.com", "name": "MyTestTeam"})

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_get_team_method_with_non_existing_team(
        self, mock_fetch_url, mock_get_version
    ):
        with set_module_args(
            {
                "state": "present",
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
            }
        ):
            module = grafana_team.setup_module_object()
            mock_fetch_url.return_value = team_not_found_resp()
            mock_get_version.return_value = get_version_resp()

            grafana_iface = grafana_team.GrafanaTeamInterface(module)
            res = grafana_iface.get_team("MyTestTeam")
            self.assertEqual(mock_fetch_url.call_count, 2)
            mock_fetch_url.assert_called_with(
                module,
                "http://grafana.example.com/api/teams/search?name=MyTestTeam",
                data=None,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": self.authorization,
                },
                method="GET",
            )
            self.assertEqual(res, None)

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_create_team_method(self, mock_fetch_url, mock_get_version):
        with set_module_args(
            {
                "state": "present",
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
            }
        ):
            module = grafana_team.setup_module_object()
            mock_fetch_url.return_value = team_created_resp()
            mock_get_version.return_value = get_version_resp()

            grafana_iface = grafana_team.GrafanaTeamInterface(module)

            res = grafana_iface.create_team("MyTestTeam", "email@test.com")
            self.assertEqual(mock_fetch_url.call_count, 2)
            mock_fetch_url.assert_called_with(
                module,
                "http://grafana.example.com/api/teams",
                data=json.dumps(
                    {"email": "email@test.com", "name": "MyTestTeam"}, sort_keys=True
                ),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": self.authorization,
                },
                method="POST",
            )
            self.assertEqual(res, {"message": "Team created", "teamId": 2})

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_update_team_method(self, mock_fetch_url, mock_get_version):
        with set_module_args(
            {
                "state": "present",
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
            }
        ):
            module = grafana_team.setup_module_object()
            mock_fetch_url.return_value = team_updated_resp()
            mock_get_version.return_value = get_version_resp()

            grafana_iface = grafana_team.GrafanaTeamInterface(module)
            res = grafana_iface.update_team(2, "MyTestTeam", "email@test.com")
            self.assertEqual(mock_fetch_url.call_count, 2)
            mock_fetch_url.assert_called_with(
                module,
                "http://grafana.example.com/api/teams/2",
                data=json.dumps(
                    {"email": "email@test.com", "name": "MyTestTeam"}, sort_keys=True
                ),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": self.authorization,
                },
                method="PUT",
            )
            self.assertEqual(res, {"message": "Team updated"})

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_delete_team_method(self, mock_fetch_url, mock_get_version):
        with set_module_args(
            {
                "state": "absent",
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
            }
        ):
            module = grafana_team.setup_module_object()
            mock_fetch_url.return_value = team_deleted_resp()
            mock_get_version.return_value = get_version_resp()

            grafana_iface = grafana_team.GrafanaTeamInterface(module)
            res = grafana_iface.delete_team(2)
            self.assertEqual(mock_fetch_url.call_count, 2)
            mock_fetch_url.assert_called_with(
                module,
                "http://grafana.example.com/api/teams/2",
                data=None,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": self.authorization,
                },
                method="DELETE",
            )
            self.assertEqual(res, {"message": "Team deleted"})

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_get_team_members_method(self, mock_fetch_url, mock_get_version):
        with set_module_args(
            {
                "state": "present",
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
            }
        ):
            module = grafana_team.setup_module_object()
            mock_fetch_url.return_value = team_members_resp()
            mock_get_version.return_value = get_version_resp()

            grafana_iface = grafana_team.GrafanaTeamInterface(module)
            res = grafana_iface.get_team_members(2)
            self.assertEqual(mock_fetch_url.call_count, 2)
            mock_fetch_url.assert_called_with(
                module,
                "http://grafana.example.com/api/teams/2/members",
                data=None,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": self.authorization,
                },
                method="GET",
            )
            self.assertEqual(res, ["user1@email.com", "user2@email.com"])

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_get_team_members_method_no_members_returned(
        self, mock_fetch_url, mock_get_version
    ):
        with set_module_args(
            {
                "state": "present",
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
            }
        ):
            module = grafana_team.setup_module_object()
            mock_fetch_url.return_value = team_members_no_members_resp()
            mock_get_version.return_value = get_version_resp()

            grafana_iface = grafana_team.GrafanaTeamInterface(module)
            res = grafana_iface.get_team_members(2)
            self.assertEqual(mock_fetch_url.call_count, 2)
            mock_fetch_url.assert_called_with(
                module,
                "http://grafana.example.com/api/teams/2/members",
                data=None,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": self.authorization,
                },
                method="GET",
            )
            self.assertEqual(res, [])

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_add_team_member_method(self, mock_fetch_url, mock_get_version):
        with set_module_args(
            {
                "state": "present",
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
            }
        ):
            module = grafana_team.setup_module_object()
            mock_fetch_url.return_value = add_team_member_resp()
            mock_get_version.return_value = get_version_resp()

            grafana_iface = grafana_team.GrafanaTeamInterface(module)
            with patch.object(
                grafana_team.GrafanaTeamInterface, "get_user_id_from_mail"
            ) as mock_get_user_id_from_mail:
                mock_get_user_id_from_mail.return_value = 42
                res = grafana_iface.add_team_member(2, "another@test.com")
                self.assertEqual(mock_fetch_url.call_count, 2)
                mock_fetch_url.assert_called_with(
                    module,
                    "http://grafana.example.com/api/teams/2/members",
                    data=json.dumps({"userId": 42}),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": self.authorization,
                    },
                    method="POST",
                )
                self.assertEqual(res, None)

    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.GrafanaTeamInterface.get_version"
    )
    @patch(
        "ansible_collections.community.grafana.plugins.modules.grafana_team.fetch_url"
    )
    def test_delete_team_member_method(self, mock_fetch_url, mock_get_version):
        with set_module_args(
            {
                "state": "present",
                "name": "MyTestTeam",
                "email": "email@test.com",
                "url": "http://grafana.example.com",
            }
        ):
            module = grafana_team.setup_module_object()
            mock_fetch_url.return_value = delete_team_member_resp()
            mock_get_version.return_value = get_version_resp()

            grafana_iface = grafana_team.GrafanaTeamInterface(module)
            with patch.object(
                grafana_team.GrafanaTeamInterface, "get_user_id_from_mail"
            ) as mock_get_user_id_from_mail:
                mock_get_user_id_from_mail.return_value = 42
                res = grafana_iface.delete_team_member(2, "another@test.com")
                self.assertEqual(mock_fetch_url.call_count, 2)
                mock_fetch_url.assert_called_with(
                    module,
                    "http://grafana.example.com/api/teams/2/members/42",
                    data=None,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": self.authorization,
                    },
                    method="DELETE",
                )
                self.assertEqual(res, None)

    def test_diff_members_function(self):
        list1 = ["foo@example.com", "bar@example.com"]
        list2 = ["bar@example.com", "random@example.com"]

        res = grafana_team.diff_members(list1, list2)
        self.assertEqual(
            res, {"to_del": ["random@example.com"], "to_add": ["foo@example.com"]}
        )
