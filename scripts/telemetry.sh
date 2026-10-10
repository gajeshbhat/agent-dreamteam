#!/usr/bin/env bash
# Sample rig/Ollama/memory every 5s into runs/<id>/samples.jsonl; `stop` collects transcripts and Ollama log.
# usage: telemetry.sh start <run-id> | stop <run-id>
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cmd=${1:?start|stop}; id=${2:?run-id}
out="$root/runs/$id"; mkdir -p "$out"
log="$HOME/.ollama/logs/server.log"
case $cmd in
start)
  wc -c < "$log" > "$out/ollama-log.offset"
  date -u +%FT%TZ > "$out/started"
  ( while :; do
      python3 -I - "$out/samples.jsonl" <<'PY'
import json,subprocess,sys,time,urllib.request
def sh(c): return subprocess.run(c,shell=True,capture_output=True,text=True).stdout
try: ps=json.load(urllib.request.urlopen("http://127.0.0.1:11434/api/ps",timeout=3))
except Exception as e: ps={"error":str(e)}
vm=sh("vm_stat"); mp=sh("memory_pressure -Q")
rig=sh("rig ps --nodes --rig dreamteam --json 2>/dev/null")
try: rig=json.loads(rig)
except Exception: rig=rig.strip()
open(sys.argv[1],"a").write(json.dumps({"ts":time.time(),"ollama":ps,"vm_stat":vm,"memory_pressure":mp,"rig":rig})+"\n")
PY
      sleep 5
    done ) & echo $! > "$out/pid"
  echo "telemetry started: $out" ;;
stop)
  [ -f "$out/pid" ] && kill "$(cat "$out/pid")" 2>/dev/null || true
  date -u +%FT%TZ > "$out/stopped"
  tail -c +"$(( $(cat "$out/ollama-log.offset") + 1 ))" "$log" > "$out/ollama-server.log"
  mkdir -p "$out/transcripts"
  for s in lead-claude builders-pi-1 builders-pi-2 builders-opencode review-pi; do
    rig transcript "$s@dreamteam" --tail 100000 > "$out/transcripts/$s.txt" 2>&1 || true
    tmux capture-pane -p -S - -t "$s@dreamteam" > "$out/transcripts/$s.pane.txt" 2>&1 || true
  done
  cp -R "$HOME/.openrig/state/pi" "$out/pi-state" 2>/dev/null || true
  git -C "$root" status --short > "$out/git-status.txt"
  find "$root/rigs/workspace" -type f -not -path '*/.build/*' -not -path '*/.git/*' -printf '' 2>/dev/null || find "$root/rigs/workspace" -type f -not -path '*/.build/*' > "$out/workspace-files.txt"
  echo "telemetry stopped: $out" ;;
esac
