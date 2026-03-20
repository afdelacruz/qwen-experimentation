#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: scripts/prime/upload_project.sh <sandbox-id>"
  exit 1
fi

SANDBOX_ID="$1"

prime sandbox upload "$SANDBOX_ID" pyproject.toml /workspace/pyproject.toml
prime sandbox upload "$SANDBOX_ID" README.md /workspace/README.md

while IFS= read -r file; do
  remote_path="/workspace/$file"
  prime sandbox upload "$SANDBOX_ID" "$file" "$remote_path"
done < <(find src -type f | sort)
