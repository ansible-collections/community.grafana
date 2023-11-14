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
from ansible.module_utils.urls import fetch_url, url_argument_spec
from ansible.module_utils._text import to_text

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


class BaseInterface:
    def check_required_version(self, minimum_version):
        if not self._module.params.get("skip_version_check"):
            try:
                response, info = fetch_url(
                    self._module,
                    "%s/api/health" % (self.grafana_url),
                    headers=self.headers,
                    method="GET",
                )
                content = json.loads(response.read())
                version = content.get("version")
                major_version = int(version.split(".")[0])

            except GrafanaError as e:
                self._module.fail_json(failed=True, msg=to_text(e))

            if major_version < int(minimum_version):
                self._module.fail_json(
                    failed=True,
                    msg="Need at least Grafana version %s to use this feature."
                    % minimum_version,
                )
