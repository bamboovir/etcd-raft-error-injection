#!/usr/bin/env bash

set -o pipefail
set -o errexit
set -o xtrace

if ! [ -x "$(command -v git)" ]; then
    printf "%s\n" 'Error: git is not installed.' >&2
    exit 1
fi

if ! [ -x "$(command -v docker)" ]; then
    printf "%s\n" 'Error: docker is not installed.' >&2
    exit 1
fi

PROJECT_ROOT=$(git rev-parse --show-toplevel)
bash "${PROJECT_ROOT}/raft/script/raft/build.bash"

docker buildx build "${PROJECT_ROOT}/raft/bin" -f "${PROJECT_ROOT}/raft/docker/Dockerfile.arm64" -t raft:dev