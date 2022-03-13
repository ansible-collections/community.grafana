from __future__ import (absolute_import, division, print_function)

from unittest import TestCase
from unittest.mock import patch, MagicMock
from ansible_collections.community.grafana.plugins.modules import grafana_plugin
import json
from ansible.module_utils._text import to_bytes
from ansible.module_utils import basic

__metaclass__ = type

def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)

def run_command_ls():
    STDERR = ""
    STDOUT = """
installed plugins:
alexanderzobnin-zabbix-app @ 3.10.5

Restart grafana after installing plugins . <service grafana-server restart>
"""
    return 0, STDOUT, STDERR


def run_command_install_zip():
    STDERR = ""
    STDOUT = """
installing alexanderzobnin-grafana-zabbix @ 
from: /home/grafana//alexanderzobnin-grafana-zabbix-v3.10.5-1-g2219691.zip
into: /var/lib/grafana/plugins

... Installed alexanderzobnin-grafana-zabbix successfully

Restart grafana after installing plugins . <service grafana-server restart>

"""
    return 0, STDOUT, STDERR


def run_command_uninstall():
    STDERR = ""
    STDOUT = """
Removing plugin: alexanderzobnin-zabbix-app

Restart grafana after installing plugins . <service grafana-server restart>
"""
    return 0, STDOUT, STDERR


def run_command_uninstall_again():
    STDERR = ""
    STDOUT = """
Removing plugin: alexanderzobnin-zabbix-app
Error: ✗ plugin does not exist
"""
    return 1, STDOUT, STDERR

def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass

class GrafanaPlugin(TestCase):

    def setUp(self):
#        self.authorization = basic_auth_header("admin", "admin")
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)

        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    @patch('ansible_collections.community.grafana.plugins.modules.grafana_plugin.grafana_cli_bin')
    def test_plugin_install_zip(self, mock_grafana_cli_bin):
        mock_grafana_cli_bin.return_value = "grafana-cli plugins"

        params = {
            "name": "alexanderzobnin-zabbix-app"
        }

        module = MagicMock()
        module.run_command.return_value = run_command_install_zip()

        result = grafana_plugin.get_grafana_plugin_version(module, params)
        self.assertEqual(result, None)

    @patch('ansible_collections.community.grafana.plugins.modules.grafana_plugin.grafana_cli_bin')
    def test_plugin_ls(self, mock_grafana_cli_bin):
        mock_grafana_cli_bin.return_value = "grafana-cli plugins"

        params = {
            "name": "alexanderzobnin-zabbix-app"
        }

        module = MagicMock()
        module.run_command.return_value = run_command_ls()

        result = grafana_plugin.get_grafana_plugin_version(module, params)
        self.assertEqual(result, "3.10.5")

    @patch('ansible_collections.community.grafana.plugins.modules.grafana_plugin.grafana_cli_bin')
    def test_plugin_uninstall(self, mock_grafana_cli_bin):
        mock_grafana_cli_bin.return_value = "grafana-cli plugins"

        params = {
            "name": "alexanderzobnin-zabbix-app"
        }

        module = MagicMock()
        module.run_command.return_value = run_command_uninstall()

        result = grafana_plugin.get_grafana_plugin_version(module, params)
        self.assertEqual(result, None)

    @patch('ansible_collections.community.grafana.plugins.modules.grafana_plugin.grafana_cli_bin')
    def test_plugin_uninstall_again(self, mock_grafana_cli_bin):
        mock_grafana_cli_bin.return_value = "grafana-cli plugins"

        params = {
            "name": "alexanderzobnin-zabbix-app"
        }

        module = MagicMock()
        module.run_command.return_value = run_command_uninstall_again()

        result = grafana_plugin.get_grafana_plugin_version(module, params)
        self.assertEqual(result, None)

    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_install_plugin(self, mock_run_command):
        grafana_plugin.grafana_cli_bin = MagicMock()
        grafana_plugin.grafana_cli_bin.return_value = "/usr/local/bin/grafana-cli plugins"
        mock_run_command.return_value = (0, "", "")

        set_module_args({
            "name": "whatever"
        })
        module = grafana_plugin.setup_module_object()
        grafana = grafana_plugin.GrafanaPluginInterface(module)

        grafana.install_plugin("whatever", "1.0.0")
        module.run_command.assert_called_with("/usr/local/bin/grafana-cli plugins install whatever 1.0.0")

    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_install_plugin_failure(self, mock_run_command):
        grafana_plugin.grafana_cli_bin = MagicMock()
        grafana_plugin.grafana_cli_bin.return_value = "/usr/local/bin/grafana-cli plugins"
        mock_run_command.return_value = (1, "mocked_stdout", "mocked_stderr")

        set_module_args({
            "name": "whatever"
        })
        module = grafana_plugin.setup_module_object()
        grafana = grafana_plugin.GrafanaPluginInterface(module)

        with self.assertRaises(AnsibleFailJson) as err:
            grafana.install_plugin("whatever", "1.0.0")
            self.assertEqual(err.stdout, "mocked_stdout")
            self.assertEqual(err.stderr, "mocked_stderr")

    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_update_plugin(self, mock_run_command):
        grafana_plugin.grafana_cli_bin = MagicMock()
        grafana_plugin.grafana_cli_bin.return_value = "/usr/local/bin/grafana-cli plugins"
        mock_run_command.return_value = (0, "", "")

        set_module_args({
            "name": "whatever"
        })
        module = grafana_plugin.setup_module_object()
        grafana = grafana_plugin.GrafanaPluginInterface(module)

        grafana.update_plugin("whatever", "1.0.0")
        module.run_command.assert_called_with("/usr/local/bin/grafana-cli plugins update whatever 1.0.0")

    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_update_plugin_failure(self, mock_run_command):
        grafana_plugin.grafana_cli_bin = MagicMock()
        grafana_plugin.grafana_cli_bin.return_value = "/usr/local/bin/grafana-cli plugins"
        mock_run_command.return_value = (1, "mocked_stdout", "mocked_stderr")

        set_module_args({
            "name": "whatever"
        })
        module = grafana_plugin.setup_module_object()
        grafana = grafana_plugin.GrafanaPluginInterface(module)

        with self.assertRaises(AnsibleFailJson) as err:
            grafana.update_plugin("whatever", "1.0.0")
            self.assertEqual(err.stdout, "mocked_stdout")
            self.assertEqual(err.stderr, "mocked_stderr")

    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_delete_plugin(self, mock_run_command):
        grafana_plugin.grafana_cli_bin = MagicMock()
        grafana_plugin.grafana_cli_bin.return_value = "/usr/local/bin/grafana-cli plugins"
        mock_run_command.return_value = (0, "", "")

        set_module_args({
            "name": "whatever",
            "state": "absent"
        })
        module = grafana_plugin.setup_module_object()
        grafana = grafana_plugin.GrafanaPluginInterface(module)

        grafana.delete_plugin("whatever")
        module.run_command.assert_called_with("/usr/local/bin/grafana-cli plugins uninstall whatever")

    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_delete_plugin_not_found(self, mock_run_command):
        grafana_plugin.grafana_cli_bin = MagicMock()
        grafana_plugin.grafana_cli_bin.return_value = "/usr/local/bin/grafana-cli plugins"
        mock_run_command.return_value = (1, "blah blah plugin does not exist blah blah", "mocked_stderr")

        set_module_args({
            "name": "whatever",
            "state": "absent"
        })
        module = grafana_plugin.setup_module_object()
        grafana = grafana_plugin.GrafanaPluginInterface(module)

        grafana.delete_plugin("whatever")
        module.run_command.assert_called_with("/usr/local/bin/grafana-cli plugins uninstall whatever")

    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_delete_plugin_failure(self, mock_run_command):
        grafana_plugin.grafana_cli_bin = MagicMock()
        grafana_plugin.grafana_cli_bin.return_value = "/usr/local/bin/grafana-cli plugins"
        mock_run_command.return_value = (1, "mocked_stdout", "mocked_stderr")

        set_module_args({
            "name": "whatever",
            "state": "absent"
        })
        module = grafana_plugin.setup_module_object()
        grafana = grafana_plugin.GrafanaPluginInterface(module)

        with self.assertRaises(AnsibleFailJson) as err:
            grafana.delete_plugin("whatever")
            self.assertEqual(err.stdout, "mocked_stdout")
            self.assertEqual(err.stderr, "mocked_stderr")

    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_delete_plugin(self, mock_run_command):
        grafana_plugin.grafana_cli_bin = MagicMock()
        grafana_plugin.grafana_cli_bin.return_value = "/usr/local/bin/grafana-cli plugins"
        mock_run_command.return_value = (0, "", "")

        set_module_args({
            "name": "whatever",
            "state": "absent"
        })
        module = grafana_plugin.setup_module_object()
        grafana = grafana_plugin.GrafanaPluginInterface(module)

        grafana.delete_plugin("whatever")
        module.run_command.assert_called_with("/usr/local/bin/grafana-cli plugins uninstall whatever")
