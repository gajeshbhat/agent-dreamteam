#!/usr/bin/env bash
# Test scripts/oneshot.sh against a fake `pi` on PATH. No model needed.
set -uo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
fail=0; check() { if eval "$2"; then echo "ok   $1"; else echo "FAIL $1"; fail=1; fi; }
mkdir -p "$tmp/bin" "$tmp/work" "$tmp/agent"
cat > "$tmp/bin/pi" <<'FAKE'
#!/usr/bin/env bash
echo "ENV_DIR=${PI_CODING_AGENT_DIR:-} ARGS=$*" >> "$FAKE_PI_LOG"
if [ -n "${FAKE_PI_HANG:-}" ]; then sleep 60 & echo $! > "$FAKE_PI_CHILD"; wait; fi
[ -n "${FAKE_PI_WRITE:-}" ] && printf '%s\n' "$FAKE_PI_WRITE" > solution.txt
echo "pi finished"
FAKE
chmod +x "$tmp/bin/pi"
export PATH="$tmp/bin:$PATH" FAKE_PI_LOG="$tmp/pi.log" DELEGATE_LOG="$tmp/log.jsonl" ONESHOT_AGENT_DIR="$tmp/agent" ONESHOT_LOG_DIR="$tmp/logs"
S="$root/scripts/oneshot.sh"

# 1. worker output satisfies the check -> exit 0, row logged, fresh no-session pi, isolated agent dir
export FAKE_PI_WRITE=good
out=$("$S" "make solution.txt" --cwd "$tmp/work" --model qwen3-coder-32k --check 'grep -qx good solution.txt' --timeout 10 2>&1); rc=$?
check "exit 0 when check passes"        "[ $rc -eq 0 ]"
check "uses --no-session and the model" "grep -q -- '--no-session' \"$tmp/pi.log\" && grep -q 'qwen3-coder-32k' \"$tmp/pi.log\""
check "uses the isolated agent dir"     "grep -q \"ENV_DIR=$tmp/agent\" \"$tmp/pi.log\""
check "logs a oneshot row"              "grep -q '\"mode\":\"oneshot\"' \"$tmp/log.jsonl\" && grep -q '\"status\":\"check-passed\"' \"$tmp/log.jsonl\""
check "output mentions check passed"    "echo \"\$out\" | grep -q 'CHECK PASSED'"

check "worker output log is kept"       "ls \"$tmp\"/logs/*.log >/dev/null 2>&1 && grep -q 'pi finished' \"$tmp\"/logs/*.log"

check "log dir is private (700)"        "[ \"\$(stat -f %Lp \"$tmp/logs\")\" = 700 ]"
check "log file is private (600)"       "[ \"\$(stat -f %Lp \"$tmp\"/logs/*.log | sort -u)\" = 600 ]"

# 2. wrong output -> exit 1
export FAKE_PI_WRITE=bad; rm -f "$tmp/work/solution.txt"
"$S" "x" --cwd "$tmp/work" --check 'grep -qx good solution.txt' --timeout 10 >/dev/null 2>&1; rc=$?
check "exit 1 when check fails"         "[ $rc -eq 1 ]"

# 3. hang -> exit 2 inside the timeout
unset FAKE_PI_WRITE; export FAKE_PI_HANG=1; t0=$(date +%s)
"$S" "x" --cwd "$tmp/work" --check 'true' --timeout 2 >/dev/null 2>&1; rc=$?; took=$(( $(date +%s)-t0 ))
check "exit 2 on hang (took ${took}s)"  "[ $rc -eq 2 ] && [ $took -le 6 ]"
unset FAKE_PI_HANG

# 3b. a hanging CHECK must not outlive --timeout either
unset FAKE_PI_WRITE; t0=$(date +%s)
"$S" "x" --cwd "$tmp/work" --check 'sleep 30' --timeout 2 >/dev/null 2>&1; rc=$?; took=$(( $(date +%s)-t0 ))
check "hanging check respects timeout (took ${took}s)" "[ $rc -eq 2 ] && [ $took -le 6 ]"

# 3c. timeout must kill the whole process tree, not just pi
export FAKE_PI_HANG=1 FAKE_PI_CHILD="$tmp/child.pid"; rm -f "$FAKE_PI_CHILD"
"$S" "x" --cwd "$tmp/work" --check 'true' --timeout 2 >/dev/null 2>&1
sleep 1; cp=$(cat "$FAKE_PI_CHILD" 2>/dev/null)
check "grandchild of pi is killed on timeout" "[ -n \"$cp\" ] && ! kill -0 $cp 2>/dev/null"
[ -n "$cp" ] && kill "$cp" 2>/dev/null; unset FAKE_PI_HANG

# 4. usage
"$S" >/dev/null 2>&1; rc=$?
check "exit 64 without args"            "[ $rc -eq 64 ]"
exit $fail
