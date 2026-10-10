#!/usr/bin/env bash
# Prove every task's check passes with its reference solution and fails on an empty one.
set -uo pipefail
root=$(cd "$(dirname "$0")/.." && pwd); bad=0
for t in "$root"/bench/tasks/*/; do
  id=$(basename "$t"); w=$(mktemp -d)
  cp "$t/check.py" "$w/"; : > "$w/solution.py"
  "$root/bench/grade.sh" "$t" "$w" && { echo "FAIL $id: passes with empty solution"; bad=1; }
  cp "$t/ref.py" "$w/solution.py"
  "$root/bench/grade.sh" "$t" "$w" && echo "ok   $id" || { echo "FAIL $id: reference does not pass"; bad=1; }
  rm -rf "$w"
done
# a solution that fakes the success line and exits must NOT be graded as a pass
w=$(mktemp -d); t="$root/bench/tasks/t1-slugify"; cp "$t/check.py" "$w/"
printf "print('OK', flush=True)\nimport os\nos._exit(0)\n" > "$w/solution.py"
"$root/bench/grade.sh" "$t" "$w" >/dev/null 2>&1 && { echo "FAIL cheater passes grading"; bad=1; } || echo "ok   cheater is rejected"
# a solution that reads the nonce file named in the environment must NOT pass either
printf "import os\nn=open(os.environ['CHECK_NONCE_FILE']).read().strip()\nprint('OK '+n, flush=True)\nos._exit(0)\n" > "$w/solution.py"
"$root/bench/grade.sh" "$t" "$w" >/dev/null 2>&1 && { echo "FAIL nonce reader passes grading"; bad=1; } || echo "ok   nonce reader is rejected"
# a solution that walks the caller's stack frames to steal the nonce must NOT pass
cat > "$w/solution.py" <<'PY'
import sys, os
def _find():
    f = sys._getframe(1)
    while f:
        v = f.f_locals.get('nonce')
        if v: return v
        f = f.f_back
print('OK ' + (_find() or ''), flush=True)
os._exit(0)
PY
"$root/bench/grade.sh" "$t" "$w" >/dev/null 2>&1 && { echo "FAIL frame inspector passes grading"; bad=1; } || echo "ok   frame inspector is rejected"

# a solution whose results compare equal to everything must NOT pass
cat > "$w/solution.py" <<'PY'
class _Any:
    def __eq__(self, o): return True
    def __ne__(self, o): return False
    def __hash__(self): return 0
def slugify(text): return _Any()
PY
"$root/bench/grade.sh" "$t" "$w" >/dev/null 2>&1 && { echo "FAIL always-equal result passes grading"; bad=1; } || echo "ok   always-equal result is rejected"
rm -rf "$w"
exit $bad
