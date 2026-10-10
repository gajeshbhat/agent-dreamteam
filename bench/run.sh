#!/usr/bin/env bash
# usage: bench/run.sh <run-id> <seat@rig> [task-id ...]   (default: all tasks)
# Sequentially delegates each task to the seat; the pass/fail is my own re-run of the check.
set -uo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
# a Mac that idles to sleep mid-run stalls the worker for minutes (seen: 2 x 8.5 min)
[ -z "${CAFFEINATED:-}" ] && exec env CAFFEINATED=1 caffeinate -i "$0" "$@"
run=${1:?run-id}; seat=${2:?seat}; shift 2
ids=("$@"); [ ${#ids[@]} -eq 0 ] && ids=($(cd "$root/bench/tasks" && ls))
out="$root/runs/bench/$run.jsonl"; mkdir -p "$(dirname "$out")"
swap_pct() { sysctl -n vm.swapusage | awk '{u=$6; t=$3; gsub("M","",u); gsub("M","",t); printf "%d", (u/t)*100}'; }
for id in "${ids[@]}"; do
  # a full swap stalls everything and corrupts timings (seen: all runs hung); refuse to continue
  [ "$(swap_pct)" -ge "${BENCH_SWAP_LIMIT:-90}" ] && { echo "ABORT: swap at $(swap_pct)% (limit ${BENCH_SWAP_LIMIT:-90}%)" >&2; exit 3; }
  t="$root/bench/tasks/$id"; w="$root/runs/bench/$run/$seat/$id"
  rm -rf "$w"; mkdir -p "$w"; cp "$t/check.py" "$w/"; chmod 444 "$w/check.py"
  task="Work in $w (cd there first). Write the whole file $w/solution.py. Do not edit check.py. $(cat "$t/prompt.txt")
Done means: cd $w && python3 check.py prints OK."
  s=$(date +%s)
  chk="$root/bench/grade.sh $t $w"
  if [[ $seat == oneshot:* ]]; then   # fresh stateless pi per task
    "$root/scripts/oneshot.sh" "$task" --cwd "$w" --model "${seat#oneshot:}" --timeout "${BENCH_TIMEOUT:-300}" --check "$chk" >/dev/null 2>&1
  else
    "$root/scripts/delegate.sh" "$seat" "$task" --timeout "${BENCH_TIMEOUT:-300}" --check "$chk" >/dev/null 2>&1
  fi
  rc=$?; secs=$(( $(date +%s) - s ))
  "$root/bench/grade.sh" "$t" "$w" && pass=true || pass=false
  python3 -I - "$out" "$run" "$seat" "$id" "$(cat "$t/size")" "$rc" "$secs" "$pass" <<'PY'
import json,sys,time
o,run,seat,id,size,rc,secs,p=sys.argv[1:9]
open(o,"a").write(json.dumps({"ts":time.time(),"run":run,"seat":seat,"task":id,"size":size,"delegate_rc":int(rc),"seconds":int(secs),"passed":p=="true"},separators=(",",":"))+"\n")
PY
  echo "$id rc=$rc ${secs}s passed=$pass"
done
