# Grafana Collection Changes

## 0.2.2
  - Bug fixes:
    - Fix an issue in `grafana_dashboard` that made dashboard import no more detecting changes and fail.
  - Improvements:
    - Refactor module `grafana_datasource` to ease its support.

## 0.2.1
  - Bug fixes:
    - Fix an issue with `grafana_datasource` idempotency

## 0.2.0
  - New content:
    - Add Thruk as Grafana Datasource
    - Add `grafana_user` module
    - Add `grafana_folder` module
  - Bug fixes:
    - Fix issue #45 in `grafana_plugin`
  - Improvements:
    - Use `module_utils` to allow code factorization

## 0.1.0
  - Initial migration of Grafana content from Ansible core (2.9 / devel), including content:
    - **Connection Plugins**:
    - **Filter Plugins**:
    - **Inventory Source**:
    - **Callback Plugins**:
      - `grafana_annotations`
    - **Lookup Plugins**:
      - `grafana_dashboard`
    - **Modules**:
      - `grafana_dashboard`
      - `grafana_datasource`
      - `grafana_plugin`
