#!/usr/bin/env bash
# Run one task in a fresh, stateless `pi -p` (no carried context) and judge it with the boss's check.
# usage: oneshot.sh <task | @file> --cwd DIR --check CMD [--model M] [--timeout S]
# Exit: 0 check passed, 1 check failed, 2 timeout, 64 usage.
set -uo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
[ $# -ge 1 ] || { echo "usage: oneshot.sh <task | @file> --cwd DIR --check CMD [--model M] [--timeout S]" >&2; exit 64; }
task=$1; shift
cwd=""; check=""; model=${ONESHOT_MODEL:-qwen3-coder-32k}; timeout=300
while [ $# -gt 0 ]; do
  case $1 in
    --cwd) cwd=${2:?}; shift 2;; --check) check=${2:?}; shift 2;;
    --model) model=${2:?}; shift 2;; --timeout) timeout=${2:?}; shift 2;;
    *) echo "unknown option: $1" >&2; exit 64;;
  esac
done
[ -n "$cwd" ] && [ -n "$check" ] || { echo "oneshot.sh needs --cwd and --check" >&2; exit 64; }
case $task in @*) task=$(cat "${task#@}");; esac

# private agent dir: our models.json, your pi settings/auth (a bare dir hung pi once)
agent=${ONESHOT_AGENT_DIR:-$HOME/.openrig/state/oneshot/agent}; mkdir -p "$agent"
cp "$root/configs/pi-models.json" "$agent/models.json"
for f in settings.json auth.json; do [ -f "$HOME/.pi/agent/$f" ] && [ ! -f "$agent/$f" ] && cp "$HOME/.pi/agent/$f" "$agent/$f"; done

# worker output can contain anything the model printed: private dir, private unguessable file
logdir=${ONESHOT_LOG_DIR:-$root/runs/oneshot-logs}; ( umask 077; mkdir -p "$logdir" ); chmod 700 "$logdir"
out=$(umask 077; mktemp "$logdir/$(date +%Y%m%dT%H%M%S).XXXXXX"); mv "$out" "$out.log"; out="$out.log"
mkdir -p "$cwd"; start=$(date +%s)
# own process group (perl setpgrp) so a timeout can kill pi AND everything it spawned
( cd "$cwd" && exec env PI_CODING_AGENT_DIR="$agent" perl -e 'setpgrp(0,0); exec @ARGV' pi -p --no-session --provider ollama --model "$model" "$task" </dev/null >"$out" 2>&1 ) & pp=$!
while kill -0 "$pp" 2>/dev/null; do
  [ $(( $(date +%s) - start )) -ge "$timeout" ] && { kill -TERM -- "-$pp" 2>/dev/null; sleep 0.3; kill -KILL -- "-$pp" 2>/dev/null; wait "$pp" 2>/dev/null; status=timeout; break; }
  sleep "${ONESHOT_POLL:-0.2}"
done
secs=$(( $(date +%s) - start ))
if [ "${status:-}" != timeout ]; then
  wait "$pp" 2>/dev/null
  # cap the check at the time left (min 1 s) so a hang cannot outlive --timeout
  cf=$(mktemp); ( cd "$cwd" && bash -c "$check" >"$cf" 2>&1 ) & cp=$!
  left=$(( timeout - ( $(date +%s) - start ) )); [ "$left" -lt 1 ] && left=1
  for _ in $(seq 1 $(( left * 10 ))); do kill -0 "$cp" 2>/dev/null || break; sleep 0.1; done
  if kill -0 "$cp" 2>/dev/null; then pkill -P "$cp" 2>/dev/null; kill "$cp" 2>/dev/null; wait "$cp" 2>/dev/null; status=timeout
  elif wait "$cp"; then status=check-passed; else status=check-failed; fi
  cres=$(cat "$cf"); rm -f "$cf"
fi

python3 -I - "${DELEGATE_LOG:-$root/runs/delegations.jsonl}" "$model" "$status" "$secs" "${#task}" <<'PY'
import json,os,sys,time
log,model,status,secs,tlen=sys.argv[1:6]
os.makedirs(os.path.dirname(log),exist_ok=True)
open(log,"a").write(json.dumps({"ts":time.time(),"mode":"oneshot","seat":"oneshot:"+model,"status":status,"seconds":int(secs),"task_chars":int(tlen)},separators=(",",":"))+"\n")
PY
tail -n 15 "$out"; echo "log: $out" >&2
case $status in
  check-passed) echo "CHECK PASSED (${secs}s): $check"; exit 0;;
  timeout)      echo "TIMEOUT after ${secs}s" >&2; exit 2;;
  *)            echo "CHECK FAILED (${secs}s): $check" >&2; echo "$cres" | tail -n 5 >&2; exit 1;;
esac
