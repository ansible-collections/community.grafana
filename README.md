# Grafana Collection for Ansible

![](https://github.com/ansible-collections/grafana/workflows/CI/badge.svg?branch=master)
[![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/grafana)](https://codecov.io/gh/ansible-collections/community.grafana)
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-14-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END --> 

This repo hosts the `community.grafana` Ansible Collection.

The collection includes a variety of Ansible content to help automate the management of resources in Grafana.

## Included content

Click on the name of a plugin or module to view that content's documentation:

  - **Connection Plugins**:
  - **Filter Plugins**:
  - **Inventory Source**:
  - **Callback Plugins**:
    - [grafana_annotations](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_annotations_callback.html)
  - **Lookup Plugins**:
    - [grafana_dashboard](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_dashboard_lookup.html)
  - **Modules**:
    - [grafana_dashboard](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_dashboard_module.html)
    - [grafana_datasource](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_datasource_module.html)
    - [grafana_folder](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_folder_module.html)
    - [grafana_plugin](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_plugin_module.html)
    - [grafana_team](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_team_module.html)
    - [grafana_user](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_user_module.html)

## Supported Grafana versions

We aim at keeping the last 3 minor versions (at least) of Grafana tested.
This collection is currently testing the modules against Grafana versions `7.0.6`, `7.1.3` and `8.1.2`.

## Installation and Usage

### Installing the Collection from Ansible Galaxy

Before using the Grafana collection, you need to install it with the Ansible Galaxy CLI:

    ansible-galaxy collection install community.grafana

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: community.grafana
    version: 1.2.0
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

## Changelogs

* Every change that does not only affect docs or tests must have a changelog fragment.
  * Exception: fixing/extending a feature that already has a changelog fragment and has not yet been released. Such PRs must always link to the original PR(s) they update.
  * Use your common sense!
  * (This might change later. The trivial category should then be used to document changes which are not important enough to end up in the text version of the changelog.)
  * Fragments must not be added for new module PRs and new plugin PRs. The only exception are test and filter plugins: these are not automatically documented yet.
* The (x+1).0.0 changelog continues the x.0.0 changelog.
  * A x.y.0 changelog with y > 0 is not part of a changelog of a later X.*.* (with X > x) or x,Y,* (with Y > y) release.
  * A x.y.z changelog with z > 0 is not part of a changelog of a later (x+1).*.* or x.Y.z (with Y > y) release.
Since everything adding to the minor/patch changelogs are backports, the same changelog fragments of these minor/patch releases will be in the next major release's changelog. (This is the same behavior as in ansible/ansible.)
* Changelogs do not contain previous major releases, and only use the ancestor feature (in changelogs/changelog.yaml) to point to the previous major release.
* Changelog fragments are removed after a release is made.

See [antsibull-changelog documentation](https://github.com/ansible-community/antsibull-changelog/blob/main/docs/changelogs.rst#changelog-fragment-categories)

## More Information

For more information about Ansible's Grafana integration, join the `#ansible-community` channel on [irc.libera.chat](https://libera.chat/), and browse the resources in the [Grafana Working Group](https://github.com/ansible/community/wiki/Grafana) Community wiki page.

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
    <td align="center"><a href="https://github.com/gundalow"><img src="https://avatars1.githubusercontent.com/u/940557?v=4?s=100" width="100px;" alt=""/><br /><sub><b>John R Barker</b></sub></a><br /><a href="#infra-gundalow" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/ansible-collections/community.grafana/commits?author=gundalow" title="Tests">⚠️</a> <a href="https://github.com/ansible-collections/community.grafana/commits?author=gundalow" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/rrey"><img src="https://avatars1.githubusercontent.com/u/2752379?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Rémi REY</b></sub></a><br /><a href="https://github.com/ansible-collections/community.grafana/commits?author=rrey" title="Tests">⚠️</a> <a href="https://github.com/ansible-collections/community.grafana/commits?author=rrey" title="Documentation">📖</a> <a href="https://github.com/ansible-collections/community.grafana/commits?author=rrey" title="Code">💻</a></td>
    <td align="center"><a href="https://aperogeek.fr"><img src="https://avatars1.githubusercontent.com/u/1336359?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Thierry Sallé</b></sub></a><br /><a href="https://github.com/ansible-collections/community.grafana/commits?author=seuf" title="Code">💻</a> <a href="https://github.com/ansible-collections/community.grafana/commits?author=seuf" title="Tests">⚠️</a></td>
    <td align="center"><a href="http://antoine.tanzil.li"><img src="https://avatars0.githubusercontent.com/u/1068018?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Antoine</b></sub></a><br /><a href="https://github.com/ansible-collections/community.grafana/commits?author=Tailzip" title="Code">💻</a> <a href="https://github.com/ansible-collections/community.grafana/commits?author=Tailzip" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/pomverte"><img src="https://avatars0.githubusercontent.com/u/695230?v=4?s=100" width="100px;" alt=""/><br /><sub><b>hvle</b></sub></a><br /><a href="https://github.com/ansible-collections/community.grafana/commits?author=pomverte" title="Code">💻</a> <a href="https://github.com/ansible-collections/community.grafana/commits?author=pomverte" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/jual"><img src="https://avatars2.githubusercontent.com/u/4416541?v=4?s=100" width="100px;" alt=""/><br /><sub><b>jual</b></sub></a><br /><a href="https://github.com/ansible-collections/community.grafana/commits?author=jual" title="Code">💻</a> <a href="https://github.com/ansible-collections/community.grafana/commits?author=jual" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/MCyprien"><img src="https://avatars2.githubusercontent.com/u/11160859?v=4?s=100" width="100px;" alt=""/><br /><sub><b>MCyprien</b></sub></a><br /><a href="https://github.com/ansible-collections/community.grafana/commits?author=MCyprien" title="Code">💻</a> <a href="https://github.com/ansible-collections/community.grafana/commits?author=MCyprien" title="Tests">⚠️</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://twitter.com/RealRockaut"><img src="https://avatars0.githubusercontent.com/u/453368?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Markus Fischbacher</b></sub></a><br /><a href="https://github.com/ansible-collections/community.grafana/commits?author=rockaut" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/rverchere"><img src="https://avatars3.githubusercontent.com/u/232433?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Remi Verchere</b></sub></a><br /><a href="https://github.com/ansible-collections/community.grafana/commits?author=rverchere" title="Code">💻</a></td>
    <td align="center"><a href="http://akasurde.github.io"><img src="https://avatars1.githubusercontent.com/u/633765?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Abhijeet Kasurde</b></sub></a><br /><a href="https://github.com/ansible-collections/community.grafana/commits?author=Akasurde" title="Documentation">📖</a> <a href="https://github.com/ansible-collections/community.grafana/commits?author=Akasurde" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/martinwangjian"><img src="https://avatars2.githubusercontent.com/u/1770277?v=4?s=100" width="100px;" alt=""/><br /><sub><b>martinwangjian</b></sub></a><br /><a href="https://github.com/ansible-collections/community.grafana/commits?author=martinwangjian" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/CWollinger"><img src="https://avatars2.githubusercontent.com/u/11299733?v=4?s=100" width="100px;" alt=""/><br /><sub><b>cwollinger</b></sub></a><br /><a href="https://github.com/ansible-collections/community.grafana/commits?author=cwollinger" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/Andersson007"><img src="https://avatars3.githubusercontent.com/u/34477873?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Andrew Klychkov</b></sub></a><br /><a href="https://github.com/ansible-collections/community.grafana/commits?author=Andersson007" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/vnea"><img src="https://avatars.githubusercontent.com/u/10775422?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Victor</b></sub></a><br /><a href="https://github.com/ansible-collections/community.grafana/commits?author=vnea" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
