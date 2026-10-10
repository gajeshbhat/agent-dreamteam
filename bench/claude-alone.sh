#!/usr/bin/env bash
# Control: the same tasks, same briefs, done by a headless Claude with no workers.
# usage: bench/claude-alone.sh <run-id> [task-id ...]   (env CLAUDE_MODEL, default claude-sonnet-5-5)
set -uo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
[ -z "${CAFFEINATED:-}" ] && exec env CAFFEINATED=1 caffeinate -i "$0" "$@"
run=${1:?run-id}; shift
ids=("$@"); [ ${#ids[@]} -eq 0 ] && ids=($(cd "$root/bench/tasks" && ls))
model=${CLAUDE_MODEL:-claude-sonnet-5-5}
out="$root/runs/bench/$run.jsonl"; raw="$root/runs/bench/$run-raw"; mkdir -p "$raw"
for id in "${ids[@]}"; do
  t="$root/bench/tasks/$id"; w="$root/runs/bench/$run/claude/$id"
  rm -rf "$w"; mkdir -p "$w"; cp "$t/check.py" "$w/"; chmod 444 "$w/check.py"
  task="Work in $w (cd there first). Write the whole file $w/solution.py. Do not edit check.py. $(cat "$t/prompt.txt")
Done means: cd $w && python3 check.py prints OK."
  s=$(date +%s)
  (cd "$w" && claude -p "$task" --model "$model" --output-format json --no-session-persistence \
      --setting-sources project --disable-slash-commands --strict-mcp-config \
      --permission-mode acceptEdits \
      --allowedTools "Bash(python3:*)" "Bash(cd:*)" --disallowedTools "WebFetch" "WebSearch" "Bash(rm:*)" "Bash(curl:*)" "Bash(sh:*)" "Bash(bash:*)" \
      --max-turns 15 </dev/null) > "$raw/$id.json" 2>"$raw/$id.err"
  secs=$(( $(date +%s) - s ))
  "$root/bench/grade.sh" "$t" "$w" && pass=true || pass=false
  python3 -I - "$out" "$run" "$id" "$(cat "$t/size")" "$secs" "$pass" "$raw/$id.json" "$model" <<'PY'
import json,sys,time
o,run,id,size,secs,p,rawp,model=sys.argv[1:9]
try: d=json.load(open(rawp))
except Exception: d={}
u=d.get("usage",{})
row={"ts":time.time(),"run":run,"seat":"claude:"+model,"task":id,"size":size,"delegate_rc":0,"seconds":int(secs),"passed":p=="true",
     "turns":d.get("num_turns"),"cost_usd":d.get("total_cost_usd"),"input":u.get("input_tokens"),"output":u.get("output_tokens"),
     "cache_create":u.get("cache_creation_input_tokens"),"cache_read":u.get("cache_read_input_tokens")}
open(o,"a").write(json.dumps(row,separators=(",",":"))+"\n")
PY
  echo "$id ${secs}s passed=$pass"
done
