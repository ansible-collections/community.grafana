================================
Grafana Collection Release Notes
================================

.. contents:: Topics


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

