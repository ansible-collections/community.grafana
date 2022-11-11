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
  validate_certs:
    description:
    - Boolean variable to include --insecure while installing pluging
    default: False
    type: bool
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


def grafana_plugin(module, params):
    '''
    Install update or remove grafana plugin

    :param module: ansible module object. used to run system commands.
    :param params: ansible module params.
    '''
    grafana_cli = grafana_cli_bin(params)

    if params['state'] == 'present':
        grafana_plugin_version = get_grafana_plugin_version(module, params)
        if grafana_plugin_version is not None:
            if 'version' in params and params['version']:
                if params['version'] == grafana_plugin_version:
                    return {'msg': 'Grafana plugin already installed',
                            'changed': False,
                            'version': grafana_plugin_version}
                else:
                    if params['version'] == 'latest' or params['version'] is None:
                        latest_version = get_grafana_plugin_version_latest(module, params)
                        if latest_version == grafana_plugin_version:
                            return {'msg': 'Grafana plugin already installed',
                                    'changed': False,
                                    'version': grafana_plugin_version}
                        cmd = '{0} update {1}'.format(grafana_cli, params['name'])
                    else:
                        cmd = '{0} install {1} {2}'.format(grafana_cli, params['name'], params['version'])
            else:
                return {'msg': 'Grafana plugin already installed',
                        'changed': False,
                        'version': grafana_plugin_version}
        else:
            if 'version' in params:
                if params['version'] == 'latest' or params['version'] is None:
                    cmd = '{0} install {1}'.format(grafana_cli, params['name'])
                else:
                    cmd = '{0} install {1} {2}'.format(grafana_cli, params['name'], params['version'])
            else:
                cmd = '{0} install {1}'.format(grafana_cli, params['name'])
    else:
        cmd = '{0} uninstall {1}'.format(grafana_cli, params['name'])

    rc, stdout, stderr = module.run_command(cmd)
    if rc == 0:
        stdout_lines = stdout.split("\n")
        for line in stdout_lines:
            if line.find(params['name']):
                if line.find(' @ ') != -1:
                    line = line.rstrip()
                    plugin_name, plugin_version = parse_version(line)
                else:
                    plugin_version = None

                if params['state'] == 'present':
                    return {'msg': 'Grafana plugin {0} installed : {1}'.format(params['name'], cmd),
                            'changed': True,
                            'version': plugin_version}
                else:
                    return {'msg': 'Grafana plugin {0} uninstalled : {1}'.format(params['name'], cmd),
                            'changed': True}
    else:
        if params['state'] == 'absent' and stdout.find("plugin does not exist"):
            return {'msg': 'Grafana plugin {0} already uninstalled : {1}'.format(params['name'], cmd), 'changed': False}
        raise GrafanaCliException("'{0}' execution returned an error : [{1}] {2} {3}".format(cmd, rc, stdout, stderr))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True,
                      type='str'),
            version=dict(type='str'),
            grafana_plugins_dir=dict(type='str'),
            grafana_repo=dict(type='str'),
            grafana_plugin_url=dict(type='str'),
            validate_certs=dict(type='bool', default=False),
            state=dict(choices=['present', 'absent'],
                       default='present')
        ),
        supports_check_mode=False
    )

    try:
        result = grafana_plugin(module, module.params)
    except GrafanaCliException as e:
        module.fail_json(
            failed=True,
            msg="{0}".format(e)
        )
        return
    except Exception as e:
        module.fail_json(
            failed=True,
            msg="{0} : {1} ".format(type(e), e)
        )
        return

    module.exit_json(
        failed=False,
        **result
    )
    return


if __name__ == '__main__':
    main()
