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
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright: (c) 2019, Rémi REY (@rrey)

from __future__ import absolute_import, division, print_function
from ansible.module_utils.urls import url_argument_spec, fetch_url

import json

__metaclass__ = type


def clean_url(url):
    return url.rstrip("/")


def grafana_argument_spec():
    argument_spec = url_argument_spec()

    del argument_spec["force"]
    del argument_spec["force_basic_auth"]
    del argument_spec["http_agent"]
    # Avoid sanity error with devel
    if "use_gssapi" in argument_spec:
        del argument_spec["use_gssapi"]

    argument_spec.update(
        state=dict(choices=["present", "absent"], default="present"),
        url=dict(aliases=["grafana_url"], type="str", required=True),
        grafana_api_key=dict(type="str", no_log=True),
        url_username=dict(aliases=["grafana_user"], default="admin"),
        url_password=dict(aliases=["grafana_password"], default="admin", no_log=True),
    )
    return argument_spec


def grafana_required_together():
    return [["url_username", "url_password"]]


def grafana_mutually_exclusive():
    return [["url_username", "grafana_api_key"]]


def grafana_send_request(
    self, module, url, grafana_url, data=None, headers=None, method="GET"
):
    self.module = module
    if data is not None:
        data = json.dumps(data, sort_keys=True)
    if not headers:
        headers = []

    full_url = "{grafana_url}{path}".format(grafana_url=grafana_url, path=url)
    resp, info = fetch_url(
        module=self.module, url=full_url, data=data, headers=headers, method=method
    )
    status_code = info["status"]
    if status_code == 404:
        return None
    elif status_code == 401:
        return self._module.fail_json(
            failed=True,
            msg="Unauthorized to perform action '%s' on '%s' header: %s"
            % (method, full_url, self.headers),
        )
    elif status_code == 403:
        self._module.fail_json(failed=True, msg="Permission Denied")
    elif status_code < 0:
        self._module.fail_json(failed=True, msg=info["msg"])
    elif status_code in [200, 202]:
        return self._module.from_json(resp.read())
    self._module.fail_json(
        failed=True,
        msg="Grafana API answered with HTTP %d" % status_code,
        body=self._module.from_json(resp.read()),
    )
