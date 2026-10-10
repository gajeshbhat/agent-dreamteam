#!/usr/bin/env bash
# Start the local worker rig and attach this session as the boss. Idempotent.
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
for m in qwen3-coder-32k devstral-32k; do
  ollama list | grep -q "^$m:" || ollama create "$m" -f "$root/configs/Modelfile.$m"
done
rig status >/dev/null 2>&1 || rig daemon start --no-kernel
"$root/scripts/prepare-pi-seats.sh"
rig ps --rig workers >/dev/null 2>&1 && rig ps --nodes --rig workers 2>/dev/null | grep -q builders-pi-1 \
  || rig up "$root/rigs/workers.yaml" --yes
id=$(rig ps --rig workers --json 2>/dev/null | python3 -I -c 'import json,sys; d=json.load(sys.stdin); d=d if isinstance(d,list) else d.get("rigs",[]); print(next((r.get("rigId") or r.get("id") for r in d if r.get("name")=="workers" or r.get("rigName")=="workers"),""))')
# attach output carries a hook token, so discard it, but never hide a failure
if [ -z "$id" ] || ! rig attach --self --rig "$id" --pod builders --member boss --runtime claude-code \
     --cwd "$root" --display-name msl-claude-code >/dev/null 2>&1; then
  echo "WARNING: could not attach this session to rig 'workers'; delegations will have no sender identity" >&2
fi
rig ps --nodes --rig workers
