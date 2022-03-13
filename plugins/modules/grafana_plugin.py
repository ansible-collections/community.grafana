#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Thierry Sallé (@seuf)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

DOCUMENTATION = '''module: grafana_plugin
author:
- Thierry Sallé (@seuf)
short_description: Manage Grafana plugins via grafana-cli
description:
- Install and remove Grafana plugins.
- See U(https://grafana.com/docs/plugins/installation/) for upstream documentation.
options:
  name:
    description:
    - Name of the plugin.
    required: true
    type: str
  version:
    description:
    - Version of the plugin to install.
    - Defaults to C(latest).
    type: str
  grafana_plugins_dir:
    description:
    - Directory where the Grafana plugin will be installed.
    - If omitted, defaults to C(/var/lib/grafana/plugins).
    type: str
  grafana_repo:
    description:
    - URL to the Grafana plugin repository.
    - 'If omitted, grafana-cli will use the default value: U(https://grafana.com/api/plugins).'
    type: str
  grafana_plugin_url:
    description:
    - Full URL to the plugin zip file instead of downloading the file from U(https://grafana.com/api/plugins).
    - Requires grafana 4.6.x or later.
    type: str
  state:
    description:
    - Whether the plugin should be installed.
    choices:
    - present
    - absent
    default: present
    type: str
'''

EXAMPLES = '''
---
- name: Install/update Grafana piechart panel plugin
  community.grafana.grafana_plugin:
    name: grafana-piechart-panel
    version: latest
    state: present
'''

RETURN = '''
---
version:
  description: version of the installed/removed/updated plugin.
  type: str
  returned: always
'''

import os
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type


class GrafanaCliException(Exception):
    pass


def parse_version(string):
    name, version = string.split('@')
    return name.strip(), version.strip()


def grafana_cli_bin(params):
    '''
    Get the grafana-cli binary path with global options.
    Raise a GrafanaCliException if the grafana-cli is not present or not in PATH

    :param params: ansible module params. Used to fill grafana-cli global params.
    '''
    program = 'grafana-cli'
    grafana_cli = None

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            grafana_cli = program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                grafana_cli = exe_file
                break

    if grafana_cli is None:
        raise GrafanaCliException('grafana-cli binary is not present or not in PATH')
    else:
        if 'grafana_plugin_url' in params and params['grafana_plugin_url']:
            grafana_cli = '{0} {1} {2}'.format(grafana_cli, '--pluginUrl', params['grafana_plugin_url'])
        if 'grafana_plugins_dir' in params and params['grafana_plugins_dir']:
            grafana_cli = '{0} {1} {2}'.format(grafana_cli, '--pluginsDir', params['grafana_plugins_dir'])
        if 'grafana_repo' in params and params['grafana_repo']:
            grafana_cli = '{0} {1} {2}'.format(grafana_cli, '--repo', params['grafana_repo'])
        if 'validate_certs' in params and params['validate_certs'] is False:
            grafana_cli = '{0} {1}'.format(grafana_cli, '--insecure')

        return '{0} {1}'.format(grafana_cli, 'plugins')


def get_grafana_plugin_version(module, params):
    '''
    Fetch grafana installed plugin version. Return None if plugin is not installed.

    :param module: ansible module object. used to run system commands.
    :param params: ansible module params.
    '''
    grafana_cli = grafana_cli_bin(params)
    rc, stdout, stderr = module.run_command('{0} ls'.format(grafana_cli))
    stdout_lines = stdout.split("\n")
    for line in stdout_lines:
        if line.find(' @ ') != -1:
            line = line.rstrip()
            plugin_name, plugin_version = parse_version(line)
            if plugin_name == params['name']:
                return plugin_version
    return None


def get_grafana_plugin_version_latest(module, params):
    '''
    Fetch the latest version available from grafana-cli.
    Return the newest version number or None not found.

    :param module: ansible module object. used to run system commands.
    :param params: ansible module params.
    '''
    grafana_cli = grafana_cli_bin(params)
    rc, stdout, stderr = module.run_command('{0} list-versions {1}'.format(grafana_cli,
                                                                           params['name']))
    stdout_lines = stdout.split("\n")
    if stdout_lines[0]:
        return stdout_lines[0].rstrip()
    return None


class GrafanaPluginInterface(object):

    def __init__(self, module):
        self.module = module
        self.grafana_cli = grafana_cli_bin(module.params)

    def install_plugin(self, name, version):
        cmd = '{0} install {1} {2}'.format(self.grafana_cli, name, version)
        rc, stdout, stderr = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(msg='Failed to install plugin',
                    stdout=stdout, stderr=stderr, cmd=cmd)

    def update_plugin(self, name, version):
        cmd = '{0} update {1} {2}'.format(self.grafana_cli, name, version)
        rc, stdout, stderr = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(msg='Failed to update plugin',
                    stdout=stdout, stderr=stderr, cmd=cmd)

    def delete_plugin(self, name):
        cmd = '{0} uninstall {1}'.format(self.grafana_cli, name)
        rc, stdout, stderr = self.module.run_command(cmd)
        if rc != 0 and stdout.find("plugin does not exist") == -1:
            self.module.fail_json(msg='Failed to unintall plugin',
                    stdout=stdout, stderr=stderr, cmd=cmd)


def setup_module_object():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True,
                      type='str'),
            version=dict(type='str', default="latest"),
            grafana_plugins_dir=dict(type='str'),
            grafana_repo=dict(type='str'),
            grafana_plugin_url=dict(type='str'),
            state=dict(choices=['present', 'absent'],
                       default='present')
        ),
        supports_check_mode=False
    )
    return module

def main():

    module = setup_module_object()
    name = module.params['name']
    state = module.params['state']

    desired_version = module.params['version']
    if params['version'] == 'latest':
        desired_version = get_grafana_plugin_version_latest(module, module.params)

    current_version = get_grafana_plugin_version(module, module.params)
    grafana = GrafanaPluginInterface(module)

    if state == 'present':
        if current_version is None:
            grafana.install_plugin(name, desired_version)
        elif desired_version == current_version:
            module.exit_json(
                    msg='Grafana plugin already installed',
                    changed=True, version=desired_version)
        else:
            grafana.update_plugin(name, desired_version)
            module.exit_json(
                    msg='Grafana plugin updated',
                    changed=True, version=desired_version)
    else:
        if current_version is None:
            module.exit_json(msg='Grafana plugin already uninstalled', changed=False)
        grafana.delete_plugin(name)
        module.exit_json(msg='Grafana plugin deleted', changed=True)


if __name__ == '__main__':
    main()
