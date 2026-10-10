#!/usr/bin/env bash
# Sequential comparison suite. Runs under caffeinate (run.sh re-execs itself under it).
set -uo pipefail
root=$(cd "$(dirname "$0")/.." && pwd); cd "$root"
export BENCH_TIMEOUT=${BENCH_TIMEOUT:-300}
while pgrep -f "bench/run.sh oneshot-qwen " >/dev/null; do sleep 5; done          # let the running one finish
./bench/run.sh oneshot-devstral oneshot:devstral-32k
./bench/run.sh seat-pi1 builders-pi-1@workers
# parallel: two one-shot streams at once on disjoint tasks
t0=$(date +%s)
./bench/run.sh par-a oneshot:qwen3-coder-32k t1-slugify t3-duration t5-wrap t7-toposort &
./bench/run.sh par-b oneshot:qwen3-coder-32k t2-roman t4-lru t6-csv t8-eval &
wait
echo "PARALLEL_WALL=$(( $(date +%s) - t0 ))"
echo "SUITE_DONE"
