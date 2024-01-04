#!/usr/bin/env bash

set -eux

ansible-playbook site.yml --check
ansible-playbook site.yml
