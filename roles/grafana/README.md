# Grafana Role for Ansible Collection Community.Grafana

Configure Grafana organizations, dashboards, folders, datasources, teams and users.

## Role Variables

| Variable         | Required | Default |
| ---------------- | -------- | ------- |
| grafana_url      | yes      |
| grafana_username | yes      |
| grafana_password | yes      |
| [**grafana_users**](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_user_module.html) |
| email | no |
| is_admin | no |
| login | yes |
| name | yes |
| password | no |
| state | no |
| [**grafana_organizations**](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_organization_module.html) |
| name | yes |
| state | no |
| [**grafana_teams**](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_team_module.html) |
| email | yes |
| enforce_members | no |
| members | no |
| name | yes |
| skip_version_check | no |
| state | no |
| [**grafana_datasources**](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_datasource_module.html) |
| access | no |
| additional_json_data | no |
| additional_secure_json_data | no |
| aws_access_key | no |
| aws_assume_role_arn | no |
| aws_auth_type | no |
| aws_credentials_profile | no |
| aws_custom_metrics_namespaces | no |
| aws_default_region | no |
| aws_secret_key | no |
| azure_client | no |
| azure_cloud | no |
| azure_secret | no |
| azure_tenant | no |
| basic_auth_password | no |
| basic_auth_user | no |
| database | no |
| ds_type | no |
| ds_url | no |
| enforce_secure_data | no |
| es_version | no |
| interval | no |
| is_default | no |
| max_concurrent_shard_requests | no |
| name | yes |
| org_id | no |
| org_name | no |
| password | no |
| sslmode | no |
| state | no |
| time_field | no |
| time_interval | no |
| tls_ca_cert | no |
| tls_client_cert | no |
| tls_client_key | no |
| tls_skip_verify | no |
| trends | no |
| tsdb_resolution | no |
| tsdb_version | no |
| uid | no |
| user | no |
| with_credentials | no |
| zabbix_password | no |
| zabbix_user | no |
| [**grafana_folders**](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_folder_module.html) |
| name | yes |
| skip_version_check | no |
| state | no |
| [**grafana_dashboards**](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_dashboard_module.html) |
| commit_message | no |
| dashboard_id | no |
| dashboard_revision | no |
| folder | no |
| org_id | no |
| org_name | no |
| overwrite | no |
| path | no |
| slug | no |
| state | no |
| uid | no |
| [**grafana_organization_users**](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_organization_user_module.html) |
| login | yes |
| org_id | no |
| org_name | no |
| role | no |
| state | no |

## Example Playbook

```yaml
---
- hosts: localhost
  gather_facts: false

  vars:
    grafana_url: "https://monitoring.example.com"
    grafana_username: "api-user"
    grafana_password: "******"

    grafana_datasources:
      - name: "Loki"
        ds_type: "loki"
        ds_url: "http://127.0.0.1:3100"
        tls_skip_verify: yes
    grafana_folders:
      - name: my_service
      - name: other_service

  roles:
    - role: community.grafana.grafana
```
