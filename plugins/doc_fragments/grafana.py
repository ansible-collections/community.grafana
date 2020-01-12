# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Rémi REY (@rrey)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


class ModuleDocFragment(object):

    DOCUMENTATION = r'''options:
  url:
    description:
      - The Grafana URL.
    required: true
    type: str
    aliases: [ grafana_url ]
  url_username:
    description:
      - The Grafana user for API authentication.
    default: admin
    type: str
    aliases: [ grafana_user ]
  url_password:
    description:
      - The Grafana password for API authentication.
    default: admin
    type: str
    aliases: [ grafana_password ]
  grafana_api_key:
    description:
      - The Grafana API key.
      - If set, C(url_username) and C(url_password) will be ignored.
    type: str
  use_proxy:
    description:
      - If C(no), it will not use a proxy, even if one is defined in an environment variable on the target hosts.
    type: bool
    default: yes
  client_cert:
    description:
      - PEM formatted certificate chain file to be used for SSL client authentication.
      - This file can also include the key as well, and if the key is included, I(client_key) is not required
    type: path
  client_key:
    description:
      - PEM formatted file that contains your private key to be used for SSL client authentication.
      - If I(client_cert) contains both the certificate and key, this option is not required.
    type: path
  validate_certs:
    description:
      - If C(no), SSL certificates will not be validated.
      - This should only set to C(no) used on personally controlled sites using self-signed certificates.
      - Prior to 1.9.2 the code defaulted to C(no).
    type: bool
    default: yes
    '''
