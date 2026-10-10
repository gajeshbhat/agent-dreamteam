#!/usr/bin/env bash
# usage: grade.sh <task-dir> <workdir>   exit 0 = pass
# The check prints "OK <nonce>"; the nonce lives in a temp file outside the workdir, so a
# solution cannot pass by printing OK and exiting.
# shortcut: check.py reads and deletes the nonce file before importing the solution, but a
# solution that inspects the caller's stack frames could still find it; upgrade by moving the
# asserts into a parent process if a worker ever does that deliberately.
nf=$(mktemp); head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n' > "$nf"
nonce=$(cat "$nf")
res=$(cd "$2" && CHECK_NONCE_FILE="$nf" python3 "$1/check.py" 2>&1); rc=$?
rm -f "$nf"
[ "$rc" -eq 0 ] && [ "$(printf '%s\n' "$res" | tail -n 1)" = "OK $nonce" ]
