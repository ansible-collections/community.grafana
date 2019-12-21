#!/bin/bash -eux

set -o pipefail

# Script Collection CI
# Once working, we may move this script elsewhere - gundalow


if find tests/output/coverage/ -mindepth 1 -name '.*' -prune -o -print -quit | grep -q .; then
    stub=""

    # shellcheck disable=SC2086
    ansible-test coverage xml -v --requirements --group-by command --group-by version ${stub:+"$stub"}

    # upload coverage report to codecov.io
    for file in tests/output/coverage/coverage=*.xml; do
        flags="${file##*/coverage=}"
        flags="${flags%.xml}"
        flags="${flags//=/,}"
        flags="${flags//[^a-zA-Z0-9_,]/_}"

        bash <(curl -s https://codecov.io/bash) \
            -f "${file}" \
            -F "${flags}" \
            -t 74944dc8-d431-4ab4-915f-d45a059c1abb \ # grafana
            -X coveragepy \
            -X gcov \
            -X fix \
            -X search \
            -X xcode \
            -K \
        || echo "Failed to upload code coverage report to codecov.io: ${file}"
    done
fi
