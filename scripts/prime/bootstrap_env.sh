#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${1:-$HOME/qwen-experimentation}"

cd "$REPO_DIR"

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
pip install -e ".[remote]"
pip install --upgrade "git+https://github.com/huggingface/transformers"

mkdir -p outputs logs data/videos

if [[ -n "${HF_TOKEN:-}" ]]; then
  install -d -m 700 "$HOME/.config"
  cat > "$HOME/.config/qwen-video-experiment.env" <<EOF
export HF_TOKEN=${HF_TOKEN}
EOF
  chmod 600 "$HOME/.config/qwen-video-experiment.env"
  if ! grep -q 'qwen-video-experiment.env' "$HOME/.bashrc" 2>/dev/null; then
    printf '\n[ -f "$HOME/.config/qwen-video-experiment.env" ] && source "$HOME/.config/qwen-video-experiment.env"\n' >> "$HOME/.bashrc"
  fi
fi

echo "Bootstrap complete in $REPO_DIR"
echo "Activate with: source .venv/bin/activate"
echo "Outputs dir: $REPO_DIR/outputs"
