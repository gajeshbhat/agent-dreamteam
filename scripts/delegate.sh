#!/usr/bin/env bash
# Send a task to a rig seat and wait for its report file. Exit: 0 done, 2 timeout, 64 usage.
# usage: delegate.sh <seat@rig> <task text | @file> [--timeout SECONDS] [--check "command"]
# With --check, the boss's own command is the proof: done as soon as it exits 0 (report not required).
set -uo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
[ $# -ge 2 ] || { echo "usage: delegate.sh <seat@rig> <task | @file> [--timeout S]" >&2; exit 64; }
seat=$1; task=$2; shift 2
timeout=600; check=""
while [ $# -gt 0 ]; do
  case $1 in
    --timeout) timeout=${2:?}; shift 2;;
    --check)   check=${2:?}; shift 2;;
    *) echo "unknown option: $1" >&2; exit 64;;
  esac
done
case $task in @*) task=$(cat "${task#@}");; esac

dir=${DELEGATE_DIR:-$root/runs/delegations}; mkdir -p "$dir"
id=$(date +%Y%m%dT%H%M%S)-$$
report="$dir/$id.report.txt"; rm -f "$report"
export OPENRIG_SESSION_NAME=${OPENRIG_SESSION_NAME:-msl-claude-code}

msg="TASK from the boss (${OPENRIG_SESSION_NAME}).
$task

RULES (earlier runs failed on exactly these):
- Use absolute paths and cd to the project directory first.
- Do not claim success without evidence: paste the exact commands you ran and their output.
- When finished, or blocked, write your report to REPORT_FILE=$report
  The report starts with DONE or BLOCKED, then the commands (each on a line starting with '\$ ') and their output.
- Do not build in a directory another seat is building in; use --scratch-path <tmp dir> for swift."

start=$(date +%s)
rig send "$seat" "$msg" >/dev/null 2>&1
status=timeout
while [ $(( $(date +%s) - start )) -lt "$timeout" ]; do
  [ -s "$report" ] && { status=done; break; }
  if [ -n "$check" ]; then
    # run the check in the background and cap it at the time left, so a hang cannot outlive --timeout
    cf=$(mktemp); bash -c "$check" >"$cf" 2>&1 & cp=$!
    left=$(( timeout - ( $(date +%s) - start ) )); [ "$left" -lt 1 ] && left=1
    for _ in $(seq 1 $(( left * 10 ))); do kill -0 "$cp" 2>/dev/null || break; sleep 0.1; done
    if kill -0 "$cp" 2>/dev/null; then pkill -P "$cp" 2>/dev/null; kill "$cp" 2>/dev/null; wait "$cp" 2>/dev/null; rc=1
    else wait "$cp"; rc=$?; fi
    checkout=$(cat "$cf"); rm -f "$cf"
    [ "$rc" -eq 0 ] && { status=check-passed; break; }
  fi
  sleep "${DELEGATE_POLL:-3}"
done
secs=$(( $(date +%s) - start ))

python3 -I - "${DELEGATE_LOG:-$root/runs/delegations.jsonl}" "$seat" "$status" "$secs" "${#task}" "$report" <<'PY'
import json,os,sys,time
log,seat,status,secs,tlen,rep=sys.argv[1:7]
rlen=os.path.getsize(rep) if os.path.exists(rep) else 0
os.makedirs(os.path.dirname(log),exist_ok=True)
open(log,"a").write(json.dumps({"ts":time.time(),"seat":seat,"status":status,"seconds":int(secs),"task_chars":int(tlen),"report_chars":rlen,"report":rep},separators=(",",":"))+"\n")
PY

if [ "$status" = timeout ]; then echo "TIMEOUT after ${secs}s waiting for $seat (report: $report)" >&2; exit 2; fi
if [ "$status" = check-passed ]; then printf 'CHECK PASSED: %s\n%s\n' "$check" "$checkout"; exit 0; fi
cat "$report"
grep -q '^\$ ' "$report" || echo "NO EVIDENCE: report has no command output; verify it yourself before trusting it." >&2
exit 0
