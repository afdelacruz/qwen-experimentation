#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  cat <<'EOF'
Usage: scripts/prime/create_sandbox.sh <docker-image> [sandbox-name]

Environment variables:
  PRIME_GPU_COUNT        Default: 1
  PRIME_CPU_CORES        Default: 8
  PRIME_MEMORY_GB        Default: 32
  PRIME_DISK_SIZE_GB     Default: 80
  PRIME_TIMEOUT_MINUTES  Default: 180
EOF
  exit 1
fi

DOCKER_IMAGE="$1"
SANDBOX_NAME="${2:-qwen-video-experiment}"

prime sandbox create "$DOCKER_IMAGE" \
  --name "$SANDBOX_NAME" \
  --gpu-count "${PRIME_GPU_COUNT:-1}" \
  --cpu-cores "${PRIME_CPU_CORES:-8}" \
  --memory-gb "${PRIME_MEMORY_GB:-32}" \
  --disk-size-gb "${PRIME_DISK_SIZE_GB:-80}" \
  --timeout-minutes "${PRIME_TIMEOUT_MINUTES:-180}" \
  --yes
