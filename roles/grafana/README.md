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
| org_id | no |
| org_name | no |
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
| [**grafana_notification_channel**](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_notification_channel_module.html) |
| dingding_message_type | no |
| dingding_url | no |
| disable_resolve_message | no |
| discord_message_content | no |
| discord_url | no |
| email_addresses | no |
| email_single | no |
| googlechat_url | no |
| hipchat_api_key | no |
| hipchat_room_id | no |
| hipchat_url | no |
| include_image | no |
| is_default | no |
| kafka_topic | no |
| kafka_url | no |
| line_token | no |
| name | yes |
| opsgenie_api_key | no |
| opsgenie_auto_close | no |
| opsgenie_override_priority | no |
| opsgenie_url | no |
| org_id | no |
| pagerduty_auto_resolve | no |
| pagerduty_integration_key | no |
| pagerduty_message_in_details | no |
| pagerduty_severity | no |
| prometheus_password | no |
| prometheus_url | no |
| prometheus_username | no |
| pushover_alert_sound | no |
| pushover_api_token | no |
| pushover_devices | no |
| pushover_expire | no |
| pushover_ok_sound | no |
| pushover_priority | no |
| pushover_retry | no |
| pushover_user_key | no |
| reminder_frequency | no |
| sensu_handler | no |
| sensu_password | no |
| sensu_source | no |
| sensu_url | no |
| sensu_username | no |
| slack_icon_emoji | no |
| slack_icon_url | no |
| slack_mention_channel | no |
| slack_mention_groups | no |
| slack_mention_users | no |
| slack_recipient | no |
| slack_token | no |
| slack_url | no |
| slack_username | no |
| state | no |
| teams_url | no |
| telegram_bot_token | no |
| telegram_chat_id | no |
| threema_api_secret | no |
| threema_gateway_id | no |
| threema_recipient_id | no |
| type | yes |
| uid | no |
| victorops_auto_resolve | no |
| victorops_url | no |
| webhook_http_method | no |
| webhook_password | no |
| webhook_url | no |
| webhook_username | no |
| [**grafana_silence**](https://docs.ansible.com/ansible/latest/collections/community/grafana/grafana_silence_module.html) |
| comment | yes |
| created_by | yes |
| ends_at | yes |
| matchers | yes |
| starts_at | yes |
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
