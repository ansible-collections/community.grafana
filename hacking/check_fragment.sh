#!/bin/bash

function comment() {
    echo "No fragment detected"
    if [ -n "$PR_NUMBER" ]; then
        gh pr review "$PR_NUMBER" -r -F "$(git rev-parse --show-toplevel)/hacking/NEED_FRAGMENT"
    fi
    exit 1
}

function approve() {
    if [ -n "$PR_NUMBER" ]; then
        gh pr review "$PR_NUMBER" -a
    fi
}

FRAGMENTS=$(git fetch && git diff --name-only --diff-filter=ACMRT origin/main..HEAD | grep "changelogs/fragments")

if [ -z "$FRAGMENTS" ]; then
    comment
else
    approve
fi
