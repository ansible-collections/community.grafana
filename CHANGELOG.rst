================================
Grafana Collection Release Notes
================================

.. contents:: Topics


v1.2.3
======

Bugfixes
--------

- Fix issue with trailing '/' in provided grafana_url. The modules now support values with trailing slashes.

v1.2.2
======

Deprecated Features
-------------------

- grafana_dashboard lookup - Providing a mangled version of the API key is no longer preferred.

Bugfixes
--------

- Fix an issue with datasource uid now returned by the Grafana API (#176)
- grafana_dashboard lookup - All valid API keys can be used, not just keys ending in '=='.
- grafana_dashboard now explicitely fails if the folder doesn't exist upon creation. It would previously silently pass but not create the dashboard. (https://github.com/ansible-collections/community.grafana/issues/153)
- grafana_team now able to handle spaces and other utf-8 chars in the name parameter. (https://github.com/ansible-collections/community.grafana/issues/164)

v1.2.1
======

Bugfixes
--------

- Fix issue with grafana_user that failed to create admin user (#142)

v1.2.0
======

Major Changes
-------------

- introduce "skip_version_check" parameter in grafana_teams and grafana_folder modules (#147)

Bugfixes
--------

- Fix issue with url when grafana_url has a trailing slash (#135)
- grafana_dashboard, Fix reference before assignment issue (#146)

v1.1.0
======

Minor Changes
-------------

- Update the version where `message` alias will disappear from `grafana_dashboard`. (Now 2.0.0)

New Modules
-----------

- community.grafana.grafana_notification_channel - Manage Grafana Notification Channels

v1.0.0
======

Release Summary
---------------

Stable release for Ansible 2.10 and beyond

Major Changes
-------------

- Add changelog management for ansible 2.10 (#112)
- grafana_datasource ; adding additional_json_data param

Known Issues
------------

- grafana_datasource doesn't set password correctly (#113)

v0.2.2
======

Bugfixes
--------

- Fix an issue in `grafana_dashboard` that made dashboard import no more detecting changes and fail.
- Refactor module `grafana_datasource` to ease its support.

v0.2.1
======

Bugfixes
--------

- Fix an issue with `grafana_datasource` idempotency

v0.2.0
======

Minor Changes
-------------

- Add Thruk as Grafana Datasource
- Add `grafana_folder` module
- Add `grafana_user` module
- Use `module_utils` to allow code factorization

Bugfixes
--------

- Fix issue `#45` in `grafana_plugin`

v0.1.0
======

Release Summary
---------------

Initial migration of Grafana content from Ansible core (2.9/devel)

