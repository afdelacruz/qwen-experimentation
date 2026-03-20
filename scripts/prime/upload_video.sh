#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  cat <<'EOF'
Usage: scripts/prime/upload_video.sh <sandbox-id> <local-video-path> [category]

Examples:
  scripts/prime/upload_video.sh sbx_123 ./sample.mp4
  scripts/prime/upload_video.sh sbx_123 ./videos/foggy/clip.mp4 foggy
EOF
  exit 1
fi

SANDBOX_ID="$1"
LOCAL_VIDEO_PATH="$2"
CATEGORY="${3:-uncategorized}"
BASENAME="$(basename "$LOCAL_VIDEO_PATH")"
REMOTE_DIR="/workspace/data/videos/$CATEGORY"
REMOTE_PATH="$REMOTE_DIR/$BASENAME"

prime sandbox run "$SANDBOX_ID" -- bash -lc "mkdir -p '$REMOTE_DIR'"
prime sandbox upload "$SANDBOX_ID" "$LOCAL_VIDEO_PATH" "$REMOTE_PATH"
printf '%s\n' "$REMOTE_PATH"
