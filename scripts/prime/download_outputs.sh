#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: scripts/prime/download_outputs.sh <sandbox-id> <remote-output-path> <local-output-path>"
  exit 1
fi

SANDBOX_ID="$1"
REMOTE_OUTPUT_PATH="$2"
LOCAL_OUTPUT_PATH="$3"

mkdir -p "$(dirname "$LOCAL_OUTPUT_PATH")"
prime sandbox download "$SANDBOX_ID" "$REMOTE_OUTPUT_PATH" "$LOCAL_OUTPUT_PATH"
