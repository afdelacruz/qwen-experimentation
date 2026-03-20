#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: scripts/prime/prepare_workspace.sh <sandbox-id>"
  exit 1
fi

SANDBOX_ID="$1"

prime sandbox run "$SANDBOX_ID" -- \
  bash -lc "mkdir -p /workspace/data/videos /workspace/outputs /workspace/logs"
