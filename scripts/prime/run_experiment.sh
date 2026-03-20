#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 ]]; then
  cat <<'EOF'
Usage: scripts/prime/run_experiment.sh <sandbox-id> <remote-video-path> <prompt> <remote-output-path> [extra args...]

Example:
  scripts/prime/run_experiment.sh sbx_123 /workspace/data/videos/tranquil/example.mp4 \
    "Describe the scene, motion level, visibility, and likely obstacles." \
    /workspace/outputs/example.json \
    --model Qwen/Qwen3.5-4B --num-frames 16
EOF
  exit 1
fi

SANDBOX_ID="$1"
REMOTE_VIDEO_PATH="$2"
PROMPT="$3"
REMOTE_OUTPUT_PATH="$4"
shift 4

prime sandbox run "$SANDBOX_ID" -- \
  python -m qwen_video_experiment.run_video_prompt \
    --video "$REMOTE_VIDEO_PATH" \
    --prompt "$PROMPT" \
    --output "$REMOTE_OUTPUT_PATH" \
    "$@"
