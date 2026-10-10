#!/usr/bin/env bash
# Copy the Ollama models.json into each pi seat's agent dir (OpenRig never writes it).
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
home=${OPENRIG_HOME:-$HOME/.openrig}
rig=workers
for seat in builders-pi-1 builders-pi-2 thinker-pi; do
  d="$home/state/pi/$seat@$rig/agent"
  mkdir -p "$d"
  cp "$root/configs/pi-models.json" "$d/models.json"
  echo "ok $d/models.json"
done
