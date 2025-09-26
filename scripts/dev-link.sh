#!/usr/bin/env bash
set -euo pipefail
COMFY="${COMFY:-$HOME/ComfyUI}"
TARGET="$COMFY/custom_nodes/comfyui-xdev-nodes"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$(dirname "$TARGET")"
ln -sfn "$HERE" "$TARGET"
echo "Linked $HERE -> $TARGET"
