#!/usr/bin/env bash

set -o pipefail
set -o errexit
set -o xtrace

gofmt -s -w -l -d .
goimports -w -l -d .