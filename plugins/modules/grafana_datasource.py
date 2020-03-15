#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Thierry Sallé (@seuf)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

ANSIBLE_METADATA = {
    'status': ['preview'],
    'supported_by': 'community',
    'metadata_version': '1.1'
}

DOCUMENTATION = '''
module: grafana_datasource
author:
- Thierry Sallé (@seuf)
- Martin Wang (@martinwangjian)
- Rémi REY (@rrey)
short_description: Manage Grafana datasources
description:
- Create/update/delete Grafana datasources via API.
options:
  name:
    description:
    - The name of the datasource.
    required: true
    type: str
  ds_type:
    description:
    - The type of the datasource.
    required: true
    choices:
    - graphite
    - prometheus
    - elasticsearch
    - influxdb
    - opentsdb
    - mysql
    - postgres
    - cloudwatch
    - alexanderzobnin-zabbix-datasource
    - sni-thruk-datasource
    type: str
  ds_url:
    description:
    - The URL of the datasource.
    required: true
    type: str
  access:
    description:
    - The access mode for this datasource.
    choices:
    - direct
    - proxy
    default: proxy
    type: str
  database:
    description:
    - Name of the database for the datasource.
    - This options is required when the C(ds_type) is C(influxdb), C(elasticsearch)
      (index name), C(mysql) or C(postgres).
    required: false
    type: str
  user:
    description:
    - The datasource login user for influxdb datasources.
    type: str
  password:
    description:
    - The datasource password.
    type: str
  basic_auth_user:
    description:
    - The datasource basic auth user.
    - Setting this option with basic_auth_password will enable basic auth.
    type: str
  basic_auth_password:
    description:
    - The datasource basic auth password, when C(basic auth) is C(yes).
    type: str
  with_credentials:
    description:
    - Whether credentials such as cookies or auth headers should be sent with cross-site
      requests.
    type: bool
    default: 'no'
  tls_client_cert:
    description:
    - The client TLS certificate.
    - If C(tls_client_cert) and C(tls_client_key) are set, this will enable TLS authentication.
    - Starts with ----- BEGIN CERTIFICATE -----
    type: str
  tls_client_key:
    description:
    - The client TLS private key
    - Starts with ----- BEGIN RSA PRIVATE KEY -----
    type: str
  tls_ca_cert:
    description:
    - The TLS CA certificate for self signed certificates.
    - Only used when C(tls_client_cert) and C(tls_client_key) are set.
    type: str
  tls_skip_verify:
    description:
    - Skip the TLS datasource certificate verification.
    type: bool
    default: false
  is_default:
    description:
    - Make this datasource the default one.
    type: bool
    default: 'no'
  org_id:
    description:
    - Grafana Organisation ID in which the datasource should be created.
    - Not used when C(grafana_api_key) is set, because the C(grafana_api_key) only
      belong to one organisation.
    default: 1
    type: int
  state:
    description:
    - Status of the datasource
    choices:
    - absent
    - present
    default: present
    type: str
  es_version:
    description:
    - Elasticsearch version (for C(ds_type = elasticsearch) only)
    - Version 56 is for elasticsearch 5.6+ where you can specify the C(max_concurrent_shard_requests)
      option.
    choices:
    - 2
    - 5
    - 56
    default: 5
    type: int
  max_concurrent_shard_requests:
    description:
    - Starting with elasticsearch 5.6, you can specify the max concurrent shard per
      requests.
    default: 256
    type: int
  time_field:
    description:
    - Name of the time field in elasticsearch ds.
    - For example C(@timestamp).
    type: str
    default: '@timestamp'
  time_interval:
    description:
    - Minimum group by interval for C(influxdb) or C(elasticsearch) datasources.
    - for example C(>10s).
    type: str
  interval:
    description:
    - For elasticsearch C(ds_type), this is the index pattern used.
    choices:
    - ''
    - Hourly
    - Daily
    - Weekly
    - Monthly
    - Yearly
    type: str
  tsdb_version:
    description:
    - The opentsdb version.
    - Use C(1) for <=2.1, C(2) for ==2.2, C(3) for ==2.3.
    choices:
    - 1
    - 2
    - 3
    default: 1
    type: int
  tsdb_resolution:
    description:
    - The opentsdb time resolution.
    choices:
    - millisecond
    - second
    default: second
    type: str
  sslmode:
    description:
    - SSL mode for C(postgres) datasource type.
    choices:
    - disable
    - require
    - verify-ca
    - verify-full
    type: str
    default: disable
  trends:
    required: false
    description:
    - Use trends or not for zabbix datasource type.
    type: bool
  aws_auth_type:
    description:
    - Type for AWS authentication for CloudWatch datasource type (authType of grafana
      api)
    default: keys
    choices:
    - keys
    - credentials
    - arn
    type: str
  aws_default_region:
    description:
    - AWS default region for CloudWatch datasource type
    default: us-east-1
    type: str
    choices:
    - ap-northeast-1
    - ap-northeast-2
    - ap-southeast-1
    - ap-southeast-2
    - ap-south-1
    - ca-central-1
    - cn-north-1
    - cn-northwest-1
    - eu-central-1
    - eu-west-1
    - eu-west-2
    - eu-west-3
    - sa-east-1
    - us-east-1
    - us-east-2
    - us-gov-west-1
    - us-west-1
    - us-west-2
  aws_credentials_profile:
    description:
    - Profile for AWS credentials for CloudWatch datasource type when C(aws_auth_type)
      is C(credentials)
    default: ''
    required: false
    type: str
  aws_access_key:
    description:
    - AWS access key for CloudWatch datasource type when C(aws_auth_type) is C(keys)
    default: ''
    required: false
    type: str
  aws_secret_key:
    description:
    - AWS secret key for CloudWatch datasource type when C(aws_auth_type) is C(keys)
    default: ''
    required: false
    type: str
  aws_assume_role_arn:
    description:
    - AWS IAM role arn to assume for CloudWatch datasource type when C(aws_auth_type)
      is C(arn)
    default: ''
    required: false
    type: str
  aws_custom_metrics_namespaces:
    description:
    - Namespaces of Custom Metrics for CloudWatch datasource type
    default: ''
    required: false
    type: str
extends_documentation_fragment:
- community.grafana.basic_auth
- community.grafana.api_key
'''

EXAMPLES = '''
---
- name: Create elasticsearch datasource
  grafana_datasource:
    name: "datasource-elastic"
    grafana_url: "https://grafana.company.com"
    grafana_user: "admin"
    grafana_password: "xxxxxx"
    org_id: "1"
    ds_type: "elasticsearch"
    ds_url: "https://elastic.company.com:9200"
    database: "[logstash_]YYYY.MM.DD"
    basic_auth_user: "grafana"
    basic_auth_password: "******"
    time_field: "@timestamp"
    time_interval: "1m"
    interval: "Daily"
    es_version: 56
    max_concurrent_shard_requests: 42
    tls_ca_cert: "/etc/ssl/certs/ca.pem"

- name: Create influxdb datasource
  grafana_datasource:
    name: "datasource-influxdb"
    grafana_url: "https://grafana.company.com"
    grafana_user: "admin"
    grafana_password: "xxxxxx"
    org_id: "1"
    ds_type: "influxdb"
    ds_url: "https://influx.company.com:8086"
    database: "telegraf"
    time_interval: ">10s"
    tls_ca_cert: "/etc/ssl/certs/ca.pem"

- name: Create postgres datasource
  grafana_datasource:
    name: "datasource-postgres"
    grafana_url: "https://grafana.company.com"
    grafana_user: "admin"
    grafana_password: "xxxxxx"
    org_id: "1"
    ds_type: "postgres"
    ds_url: "postgres.company.com:5432"
    database: "db"
    user: "postgres"
    password: "iampgroot"
    sslmode: "verify-full"

- name: Create cloudwatch datasource
  grafana_datasource:
    name: "datasource-cloudwatch"
    grafana_url: "https://grafana.company.com"
    grafana_user: "admin"
    grafana_password: "xxxxxx"
    org_id: "1"
    ds_type: "cloudwatch"
    ds_url: "http://monitoring.us-west-1.amazonaws.com"
    aws_auth_type: "keys"
    aws_default_region: "us-west-1"
    aws_access_key: "speakFriendAndEnter"
    aws_secret_key: "mel10n"
    aws_custom_metrics_namespaces: "n1,n2"

- name: grafana - add thruk datasource
  grafana_datasource:
    name: "datasource-thruk"
    grafana_url: "https://grafana.company.com"
    grafana_user: "admin"
    grafana_password: "xxxxxx"
    org_id: "1"
    ds_type: "sni-thruk-datasource"
    ds_url: "https://thruk.company.com/sitename/thruk"
    basic_auth_user: "thruk-user"
    basic_auth_password: "******"
'''

RETURN = '''
---
datasource:
  description: datasource created/updated by module
  returned: changed
  type: dict
  sample: { "access": "proxy",
        "basicAuth": false,
        "database": "test_*",
        "id": 1035,
        "isDefault": false,
        "jsonData": {
            "esVersion": 5,
            "timeField": "@timestamp",
            "timeInterval": "10s",
        },
        "name": "grafana_datasource_test",
        "orgId": 1,
        "type": "elasticsearch",
        "url": "http://elastic.company.com:9200",
        "user": "",
        "password": "",
        "withCredentials": false }
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import quote
from ansible.module_utils.urls import fetch_url, url_argument_spec, basic_auth_header
from ansible_collections.community.grafana.plugins.module_utils.base import grafana_argument_spec, grafana_required_together, grafana_mutually_exclusive

__metaclass__ = type


def compare_datasources(new, current):
    del current['typeLogoUrl']
    del current['id']
    if 'version' in current:
        del current['version']
    if 'readOnly' in current:
        del current['readOnly']
    if current['basicAuth'] is False:
        del current['basicAuthUser']
        del current['basicAuthPassword']
    if 'jsonData' in current:
        if 'tlsAuth' in current['jsonData'] and current['jsonData']['tlsAuth'] is False:
            del current['secureJsonFields']
        if 'tlsAuth' not in current['jsonData']:
            del current['secureJsonFields']
    # secureJsonData contains ciphered data which we cannot compare
    if 'secureJsonData' in new:
        del new['secureJsonData']
    return dict(before=current, after=new)


def get_datasource_payload(data):
    payload = {
        'orgId': data['org_id'],
        'name': data['name'],
        'type': data['ds_type'],
        'access': data['access'],
        'url': data['ds_url'],
        'database': data['database'],
        'withCredentials': data['with_credentials'],
        'isDefault': data['is_default'],
        'user': data['user'],
        'password': data['password']
    }

    # define basic auth
    if 'basic_auth_user' in data and data['basic_auth_user'] and 'basic_auth_password' in data and data['basic_auth_password']:
        payload['basicAuth'] = True
        payload['basicAuthUser'] = data['basic_auth_user']
        payload['basicAuthPassword'] = data['basic_auth_password']
    else:
        payload['basicAuth'] = False

    # define tls auth
    json_data = {}
    if data.get('tls_client_cert') and data.get('tls_client_key'):
        json_data['tlsAuth'] = True
        if data.get('tls_ca_cert'):
            payload['secureJsonData'] = {
                'tlsCACert': data['tls_ca_cert'],
                'tlsClientCert': data['tls_client_cert'],
                'tlsClientKey': data['tls_client_key']
            }
            json_data['tlsAuthWithCACert'] = True
        else:
            payload['secureJsonData'] = {
                'tlsClientCert': data['tls_client_cert'],
                'tlsClientKey': data['tls_client_key']
            }
    else:
        json_data['tlsAuth'] = False
        json_data['tlsAuthWithCACert'] = False
        if data.get('tls_ca_cert'):
            payload['secureJsonData'] = {
                'tlsCACert': data['tls_ca_cert']
            }

    if data.get('tls_skip_verify'):
        json_data['tlsSkipVerify'] = True

    # datasource type related parameters
    if data['ds_type'] == 'elasticsearch':
        json_data['esVersion'] = data['es_version']
        json_data['timeField'] = data['time_field']
        if data.get('interval'):
            json_data['interval'] = data['interval']
        if data['es_version'] >= 56:
            json_data['maxConcurrentShardRequests'] = data['max_concurrent_shard_requests']

    if data['ds_type'] == 'elasticsearch' or data['ds_type'] == 'influxdb':
        if data.get('time_interval'):
            json_data['timeInterval'] = data['time_interval']

    if data['ds_type'] == 'opentsdb':
        json_data['tsdbVersion'] = data['tsdb_version']
        if data['tsdb_resolution'] == 'second':
            json_data['tsdbResolution'] = 1
        else:
            json_data['tsdbResolution'] = 2

    if data['ds_type'] == 'postgres':
        json_data['sslmode'] = data['sslmode']
        if data.get('password'):
            payload['secureJsonData'] = {'password': data.get('password')}

    if data['ds_type'] == 'alexanderzobnin-zabbix-datasource':
        if data.get('trends'):
            json_data['trends'] = True

    if data['ds_type'] == 'cloudwatch':
        if data.get('aws_credentials_profle'):
            payload['database'] = data.get('aws_credentials_profile')

        json_data['authType'] = data['aws_auth_type']
        json_data['defaultRegion'] = data['aws_default_region']

        if data.get('aws_custom_metrics_namespaces'):
            json_data['customMetricsNamespaces'] = data.get('aws_custom_metrics_namespaces')
        if data.get('aws_assume_role_arn'):
            json_data['assumeRoleArn'] = data.get('aws_assume_role_arn')
        if data.get('aws_access_key') and data.get('aws_secret_key'):
            payload['secureJsonData'] = {'accessKey': data.get('aws_access_key'), 'secretKey': data.get('aws_secret_key')}
    payload['jsonData'] = json_data
    return payload


class GrafanaInterface(object):

    def __init__(self, module):
        self._module = module
        self.grafana_url = module.params.get("url")
        # {{{ Authentication header
        self.headers = {"Content-Type": "application/json"}
        if module.params.get('grafana_api_key', None):
            self.headers["Authorization"] = "Bearer %s" % module.params['grafana_api_key']
        else:
            self.headers["Authorization"] = basic_auth_header(module.params['url_username'], module.params['url_password'])
            self.switch_organisation(module.params['org_id'])
        # }}}

    def _send_request(self, url, data=None, headers=None, method="GET"):
        if data is not None:
            data = json.dumps(data, sort_keys=True)
        if not headers:
            headers = []

        full_url = "{grafana_url}{path}".format(grafana_url=self.grafana_url, path=url)
        resp, info = fetch_url(self._module, full_url, data=data, headers=headers, method=method)
        status_code = info["status"]
        if status_code == 404:
            return None
        elif status_code == 401:
            self._module.fail_json(failed=True, msg="Unauthorized to perform action '%s' on '%s'" % (method, full_url))
        elif status_code == 403:
            self._module.fail_json(failed=True, msg="Permission Denied")
        elif status_code == 200:
            return self._module.from_json(resp.read())
        self._module.fail_json(failed=True, msg="Grafana API answered with HTTP %d for url %s and data %s" % (status_code, url, data))

    def switch_organisation(self, org_id):
        url = "/api/user/using/%d" % org_id
        response = self._send_request(url, headers=self.headers, method='POST')

    def datasource_by_name(self, name):
        datasource_exists = False
        ds = {}
        url = "/api/datasources/name/%s" % quote(name)
        return self._send_request(url, headers=self.headers, method='GET')

    def delete_datasource(self, name):
        url = "/api/datasources/name/%s" % quote(name)
        self._send_request(url, headers=self.headers, method='DELETE')

    def update_datasource(self, ds_id, data):
        url = "/api/datasources/%d" % ds_id
        self._send_request(url, data=data, headers=self.headers, method='PUT')

    def create_datasource(self, data):
        url = "/api/datasources"
        self._send_request(url, data=data, headers=self.headers, method='POST')


def main():
    # use the predefined argument spec for url
    argument_spec = grafana_argument_spec()

    argument_spec.update(
        name=dict(required=True, type='str'),
        ds_type=dict(choices=['graphite',
                              'prometheus',
                              'elasticsearch',
                              'influxdb',
                              'opentsdb',
                              'mysql',
                              'postgres',
                              'cloudwatch',
                              'alexanderzobnin-zabbix-datasource',
                              'sni-thruk-datasource'], required=True),
        ds_url=dict(required=True, type='str'),
        access=dict(default='proxy', choices=['proxy', 'direct']),
        database=dict(type='str', default=""),
        user=dict(default='', type='str'),
        password=dict(default='', no_log=True, type='str'),
        basic_auth_user=dict(type='str'),
        basic_auth_password=dict(type='str', no_log=True),
        with_credentials=dict(default=False, type='bool'),
        tls_client_cert=dict(type='str', no_log=True),
        tls_client_key=dict(type='str', no_log=True),
        tls_ca_cert=dict(type='str', no_log=True),
        tls_skip_verify=dict(type='bool', default=False),
        is_default=dict(default=False, type='bool'),
        org_id=dict(default=1, type='int'),
        es_version=dict(type='int', default=5, choices=[2, 5, 56]),
        max_concurrent_shard_requests=dict(type='int', default=256),
        time_field=dict(default='@timestamp', type='str'),
        time_interval=dict(type='str'),
        interval=dict(type='str', choices=['', 'Hourly', 'Daily', 'Weekly', 'Monthly', 'Yearly'], default=''),
        tsdb_version=dict(type='int', default=1, choices=[1, 2, 3]),
        tsdb_resolution=dict(type='str', default='second', choices=['second', 'millisecond']),
        sslmode=dict(default='disable', choices=['disable', 'require', 'verify-ca', 'verify-full']),
        trends=dict(default=False, type='bool'),
        aws_auth_type=dict(default='keys', choices=['keys', 'credentials', 'arn']),
        aws_default_region=dict(default='us-east-1', choices=['ap-northeast-1', 'ap-northeast-2', 'ap-southeast-1', 'ap-southeast-2', 'ap-south-1',
                                                              'ca-central-1',
                                                              'cn-north-1', 'cn-northwest-1',
                                                              'eu-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3',
                                                              'sa-east-1',
                                                              'us-east-1', 'us-east-2', 'us-gov-west-1', 'us-west-1', 'us-west-2']),
        aws_access_key=dict(default='', no_log=True, type='str'),
        aws_secret_key=dict(default='', no_log=True, type='str'),
        aws_credentials_profile=dict(default='', type='str'),
        aws_assume_role_arn=dict(default='', type='str'),
        aws_custom_metrics_namespaces=dict(type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[['url_username', 'url_password', 'org_id'], ['tls_client_cert', 'tls_client_key']],
        mutually_exclusive=[['url_username', 'grafana_api_key'], ['tls_ca_cert', 'tls_skip_verify']],
        required_if=[
            ['ds_type', 'opentsdb', ['tsdb_version', 'tsdb_resolution']],
            ['ds_type', 'influxdb', ['database']],
            ['ds_type', 'elasticsearch', ['database', 'es_version', 'time_field', 'interval']],
            ['ds_type', 'mysql', ['database']],
            ['ds_type', 'postgres', ['database', 'sslmode']],
            ['ds_type', 'cloudwatch', ['aws_auth_type', 'aws_default_region']],
            ['es_version', 56, ['max_concurrent_shard_requests']]
        ],
    )

    state = module.params['state']
    name = module.params['name']

    grafana_iface = GrafanaInterface(module)
    ds = grafana_iface.datasource_by_name(name)

    if state == 'present':
        payload = get_datasource_payload(module.params)
        if ds is None:
            result = grafana_iface.create_datasource(payload)
            ds = grafana_iface.datasource_by_name(name)
            module.exit_json(changed=True, datasource=ds, msg='Datasource %s created' % name)
        else:
            diff = compare_datasources(payload.copy(), ds.copy())
            if diff.get('before') == diff.get('after'):
                module.exit_json(changed=False, datasource=ds, msg='Datasource %s unchanged' % name)
            grafana_iface.update_datasource(ds.get('id'), payload)
            ds = grafana_iface.datasource_by_name(name)
            module.exit_json(changed=True, diff=diff, datasource=ds, msg='Datasource %s updated' % name)
    else:
        if ds is None:
            module.exit_json(changed=False, datasource=None, msg='Datasource %s does not exist.' % name)
        grafana_iface.delete_datasource(name)
        module.exit_json(changed=True, datasource=None, msg='Datasource %s deleted.' % name)


if __name__ == '__main__':
    main()
