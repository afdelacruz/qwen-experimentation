#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 4 ]]; then
  cat <<'EOF'
Usage: scripts/prime/bootstrap_pod.sh <host> <port> [repo-dir] [repo-url]

Examples:
  scripts/prime/bootstrap_pod.sh 157.157.221.29 43438
  scripts/prime/bootstrap_pod.sh 157.157.221.29 43438 /root/qwen-experimentation https://github.com/afdelacruz/qwen-experimentation.git

Environment:
  HF_TOKEN   Optional. If set locally, it will be written to ~/.config/qwen-video-experiment.env on the pod.
EOF
  exit 1
fi

HOST="$1"
PORT="$2"
REPO_DIR="${3:-/root/qwen-experimentation}"
REPO_URL="${4:-https://github.com/afdelacruz/qwen-experimentation.git}"

HF_EXPORT=""
if [[ -n "${HF_TOKEN:-}" ]]; then
  HF_EXPORT="export HF_TOKEN=$(printf '%q' "$HF_TOKEN"); "
fi

ssh -p "$PORT" "root@$HOST" "bash -lc '
set -euo pipefail
if [[ ! -d \"$REPO_DIR/.git\" ]]; then
  git clone \"$REPO_URL\" \"$REPO_DIR\"
else
  git -C \"$REPO_DIR\" pull --ff-only
fi
$HF_EXPORT
bash \"$REPO_DIR/scripts/prime/bootstrap_env.sh\" \"$REPO_DIR\"
'"
