#!/usr/bin/env bash
# Start `ollama serve` with settings that suit a shared 32 GB laptop, logging to runs/ollama-server.log.
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd); mkdir -p "$root/runs"
if curl -sf -m 2 127.0.0.1:11434/api/version >/dev/null; then echo "ollama already serving"; exit 0; fi
OLLAMA_KEEP_ALIVE=${OLLAMA_KEEP_ALIVE:-3m} OLLAMA_NUM_PARALLEL=${OLLAMA_NUM_PARALLEL:-2} OLLAMA_MAX_LOADED_MODELS=1 \
  nohup ollama serve >>"$root/runs/ollama-server.log" 2>&1 &
for _ in $(seq 1 30); do curl -sf -m 1 127.0.0.1:11434/api/version >/dev/null && { echo "ollama up (pid $!, keep_alive=${OLLAMA_KEEP_ALIVE:-3m}, parallel=${OLLAMA_NUM_PARALLEL:-2})"; exit 0; }; sleep 1; done
echo "ollama did not start; see runs/ollama-server.log" >&2; exit 1
