# Grafana Collection for Ansible

![](https://github.com/ansible-collections/grafana/workflows/CI/badge.svg?branch=master)
[![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/grafana)](https://codecov.io/gh/ansible-collections/grafana)
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-12-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END --> 

This repo hosts the `community.grafana` Ansible Collection.

The collection includes a variety of Ansible content to help automate the management of resources in Grafana.

## Included content

Click on the name of a plugin or module to view that content's documentation:

  - **Connection Plugins**:
  - **Filter Plugins**:
  - **Inventory Source**:
  - **Callback Plugins**:
    - [grafana_annotations](https://docs.ansible.com/ansible/latest/plugins/callback/grafana_annotations.html)
  - **Lookup Plugins**:
    - [grafana_dashboard](https://docs.ansible.com/ansible/latest/plugins/lookup/grafana_dashboard.html)
  - **Modules**:
    - [grafana_dashboard](https://docs.ansible.com/ansible/latest/modules/grafana_dashboard_module.html)
    - [grafana_datasource](https://docs.ansible.com/ansible/latest/modules/grafana_datasource_module.html)
    - grafana_folder
    - [grafana_plugin](https://docs.ansible.com/ansible/latest/modules/grafana_plugin_module.html)
    - grafana_team
    - grafana_user

## Supported Grafana versions

This collection is currently testing the modules against Grafana versions `6.4.5`, `6.5.3`, `6.6.2`.
We aim at keeping the last 3 minor versions of Grafana tested.

## Installation and Usage

### Installing the Collection from Ansible Galaxy

Before using the Grafana collection, you need to install it with the Ansible Galaxy CLI:

    ansible-galaxy collection install community.grafana

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: community.grafana
    version: v0.1.0
```

### Using modules from the Grafana Collection in your playbooks

You can either call modules by their Fully Qualified Collection Namespace (FQCN), like `community.grafana.grafana_datasource`, or you can call modules by their short name if you list the `community.grafana` collection in the playbook's `collections`, like so:

```yaml
---
- hosts: localhost
  gather_facts: false
  connection: local

  collections:
    - community.grafana

  tasks:
    - name: Ensure Influxdb datasource exists.
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
```

For documentation on how to use individual modules and other content included in this collection, please see the links in the 'Included content' section earlier in this README.

## Testing and Development

If you want to develop new content for this collection or improve what's already here, the easiest way to work on the collection is to clone it into one of the configured [`COLLECTIONS_PATHS`](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#collections-paths), and work on it there.

### Testing with `ansible-test`

The `tests` directory contains configuration for running sanity and integration tests using [`ansible-test`](https://docs.ansible.com/ansible/latest/dev_guide/testing_integration.html).

You can run the collection's test suites with the commands:

    ansible-test sanity --docker -v --color
    ansible-test integration --docker -v --color

## Publishing New Versions

The current process for publishing new versions of the Grafana Collection is manual, and requires a user who has access to the `community.grafana` namespace on Ansible Galaxy to publish the build artifact.

  1. Ensure `CHANGELOG.md` contains all the latest changes.
  2. Update `galaxy.yml` and this README's `requirements.yml` example with the new `version` for the collection.
  3. Tag the version in Git and push to GitHub.
  4. Run the following commands to build and release the new version on Galaxy:

     ```
     ansible-galaxy collection build
     ansible-galaxy collection publish ./community-grafana-$VERSION_HERE.tar.gz
     ```

After the version is published, verify it exists on the [Grafana Collection Galaxy page](https://galaxy.ansible.com/community/grafana).

## More Information

For more information about Ansible's Grafana integration, join the `#ansible-community` channel on Freenode IRC, and browse the resources in the [Grafana Working Group](https://github.com/ansible/community/wiki/Grafana) Community wiki page.

## License

GNU General Public License v3.0 or later

See LICENCE to see the full text.

## Contributing

Any contribution is welcome and we only ask contributors to:
* Provide *at least* integration tests for any contribution.
* Create an issues for any significant contribution that would change a large portion of the code base.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/gundalow"><img src="https://avatars1.githubusercontent.com/u/940557?v=4" width="100px;" alt=""/><br /><sub><b>John R Barker</b></sub></a><br /><a href="#infra-gundalow" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/ansible-collections/grafana/commits?author=gundalow" title="Tests">⚠️</a> <a href="https://github.com/ansible-collections/grafana/commits?author=gundalow" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/rrey"><img src="https://avatars1.githubusercontent.com/u/2752379?v=4" width="100px;" alt=""/><br /><sub><b>Rémi REY</b></sub></a><br /><a href="https://github.com/ansible-collections/grafana/commits?author=rrey" title="Tests">⚠️</a> <a href="https://github.com/ansible-collections/grafana/commits?author=rrey" title="Documentation">📖</a></td>
    <td align="center"><a href="https://aperogeek.fr"><img src="https://avatars1.githubusercontent.com/u/1336359?v=4" width="100px;" alt=""/><br /><sub><b>Thierry Sallé</b></sub></a><br /><a href="https://github.com/ansible-collections/grafana/commits?author=seuf" title="Code">💻</a> <a href="https://github.com/ansible-collections/grafana/commits?author=seuf" title="Tests">⚠️</a></td>
    <td align="center"><a href="http://antoine.tanzil.li"><img src="https://avatars0.githubusercontent.com/u/1068018?v=4" width="100px;" alt=""/><br /><sub><b>Antoine</b></sub></a><br /><a href="https://github.com/ansible-collections/grafana/commits?author=Tailzip" title="Code">💻</a> <a href="https://github.com/ansible-collections/grafana/commits?author=Tailzip" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/pomverte"><img src="https://avatars0.githubusercontent.com/u/695230?v=4" width="100px;" alt=""/><br /><sub><b>hvle</b></sub></a><br /><a href="https://github.com/ansible-collections/grafana/commits?author=pomverte" title="Code">💻</a> <a href="https://github.com/ansible-collections/grafana/commits?author=pomverte" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/jual"><img src="https://avatars2.githubusercontent.com/u/4416541?v=4" width="100px;" alt=""/><br /><sub><b>jual</b></sub></a><br /><a href="https://github.com/ansible-collections/grafana/commits?author=jual" title="Code">💻</a> <a href="https://github.com/ansible-collections/grafana/commits?author=jual" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/MCyprien"><img src="https://avatars2.githubusercontent.com/u/11160859?v=4" width="100px;" alt=""/><br /><sub><b>MCyprien</b></sub></a><br /><a href="https://github.com/ansible-collections/grafana/commits?author=MCyprien" title="Code">💻</a> <a href="https://github.com/ansible-collections/grafana/commits?author=MCyprien" title="Tests">⚠️</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://twitter.com/RealRockaut"><img src="https://avatars0.githubusercontent.com/u/453368?v=4" width="100px;" alt=""/><br /><sub><b>Markus Fischbacher</b></sub></a><br /><a href="https://github.com/ansible-collections/grafana/commits?author=rockaut" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/rverchere"><img src="https://avatars3.githubusercontent.com/u/232433?v=4" width="100px;" alt=""/><br /><sub><b>Remi Verchere</b></sub></a><br /><a href="https://github.com/ansible-collections/grafana/commits?author=rverchere" title="Code">💻</a></td>
    <td align="center"><a href="http://akasurde.github.io"><img src="https://avatars1.githubusercontent.com/u/633765?v=4" width="100px;" alt=""/><br /><sub><b>Abhijeet Kasurde</b></sub></a><br /><a href="https://github.com/ansible-collections/grafana/commits?author=Akasurde" title="Documentation">📖</a> <a href="https://github.com/ansible-collections/grafana/commits?author=Akasurde" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/martinwangjian"><img src="https://avatars2.githubusercontent.com/u/1770277?v=4" width="100px;" alt=""/><br /><sub><b>martinwangjian</b></sub></a><br /><a href="https://github.com/ansible-collections/grafana/commits?author=martinwangjian" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/CWollinger"><img src="https://avatars2.githubusercontent.com/u/11299733?v=4" width="100px;" alt=""/><br /><sub><b>cwollinger</b></sub></a><br /><a href="https://github.com/ansible-collections/grafana/commits?author=cwollinger" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
