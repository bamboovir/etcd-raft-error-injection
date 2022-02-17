#!/usr/bin/env bash

set -o pipefail
set -o errexit
set -o xtrace

if ! [ -x "$(command -v git)" ]; then
    printf "%s\n" 'Error: git is not installed.' >&2
    exit 1
fi

if ! [ -x "$(command -v go)" ]; then
    printf "%s\n" 'Error: go is not installed.' >&2
    exit 1
fi

PROJECT_ROOT=$(git rev-parse --show-toplevel)
go build -race -tags "" -mod=vendor -o "${PROJECT_ROOT}/raft/bin/raft" "${PROJECT_ROOT}/raft/cli/raft"