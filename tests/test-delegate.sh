#!/usr/bin/env bash
# Test scripts/delegate.sh against a fake `rig` on PATH. No daemon or model needed.
set -uo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
fail=0; check() { if eval "$2"; then echo "ok   $1"; else echo "FAIL $1"; fail=1; fi; }

mkdir -p "$tmp/bin"
# Fake rig: on `send`, record args, and write the report file named in the message.
cat > "$tmp/bin/rig" <<'FAKE'
#!/usr/bin/env bash
[ "$1" = send ] || exit 0
echo "ID=${OPENRIG_SESSION_NAME:-} ARGS=$*" >> "$FAKE_RIG_LOG"
if [ -n "${FAKE_RIG_REPORT:-}" ]; then
  out=$(printf '%s' "$*" | grep -o 'REPORT_FILE=[^ ]*' | head -1 | cut -d= -f2)
  printf '%s\n' "$FAKE_RIG_REPORT" > "$out"
fi
[ -n "${FAKE_RIG_CREATE:-}" ] && : > "$FAKE_RIG_CREATE"
FAKE
chmod +x "$tmp/bin/rig"
export PATH="$tmp/bin:$PATH" FAKE_RIG_LOG="$tmp/rig.log" DELEGATE_LOG="$tmp/delegations.jsonl" DELEGATE_POLL=0.1

# 1. happy path: report is returned, identity is stamped, a log row is written
export FAKE_RIG_REPORT="DONE: wrote /tmp/x.swift
\$ swift build
Build complete!"
out=$("$root/scripts/delegate.sh" builders-pi-1@dreamteam "write x.swift" --timeout 5); rc=$?
check "exit 0 on report"          "[ $rc -eq 0 ]"
check "report returned"           "echo \"\$out\" | grep -q 'Build complete!'"
check "sender identity stamped"   "grep -q 'ID=msl-claude-code' \"$tmp/rig.log\""
check "task has absolute-path rule" "grep -q -i 'absolute path' \"$tmp/rig.log\""
check "task asks for pasted output" "grep -q -i 'paste' \"$tmp/rig.log\""
check "log row written"           "grep -q '\"status\":\"done\"' \"$tmp/delegations.jsonl\""

# 2. timeout: no report -> exit 2 and a timeout row
unset FAKE_RIG_REPORT; : > "$tmp/delegations.jsonl"
"$root/scripts/delegate.sh" builders-pi-1@dreamteam "never answered" --timeout 1 >/dev/null 2>&1; rc=$?
check "exit 2 on timeout"         "[ $rc -eq 2 ]"
check "timeout row written"       "grep -q '\"status\":\"timeout\"' \"$tmp/delegations.jsonl\""

# 3. report without evidence is flagged
export FAKE_RIG_REPORT="DONE"
out=$("$root/scripts/delegate.sh" builders-pi-1@dreamteam "x" --timeout 5 2>&1)
check "warns when report has no command output" "echo \"\$out\" | grep -q 'NO EVIDENCE'"

# 3b. --check: done when the boss's own command passes, even with no report
unset FAKE_RIG_REPORT; export FAKE_RIG_CREATE="$tmp/made.txt"; : > "$tmp/delegations.jsonl"
out=$("$root/scripts/delegate.sh" builders-pi-1@dreamteam "make a file" --check "test -f $tmp/made.txt && echo CHECK-OK" --timeout 5 2>&1); rc=$?
check "check passing gives exit 0"  "[ $rc -eq 0 ]"
check "check output returned"       "echo \"\$out\" | grep -q CHECK-OK"
check "check-passed row written"    "grep -q '\"status\":\"check-passed\"' \"$tmp/delegations.jsonl\""
unset FAKE_RIG_CREATE; rm -f "$tmp/made.txt"
"$root/scripts/delegate.sh" builders-pi-1@dreamteam "x" --check "false" --timeout 1 >/dev/null 2>&1; rc=$?
check "failing check times out"     "[ $rc -eq 2 ]"

# 3c. a hanging check must not outlive --timeout
t0=$(date +%s)
"$root/scripts/delegate.sh" builders-pi-1@dreamteam "x" --check "sleep 30" --timeout 2 >/dev/null 2>&1; rc=$?
took=$(( $(date +%s) - t0 ))
check "hanging check respects timeout (took ${took}s)" "[ $rc -eq 2 ] && [ $took -le 6 ]"

# 4. usage error
"$root/scripts/delegate.sh" >/dev/null 2>&1; rc=$?
check "exit 64 without args"      "[ $rc -eq 64 ]"
exit $fail
