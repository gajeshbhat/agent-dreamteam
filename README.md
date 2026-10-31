# agent-dreamteam

![license](https://img.shields.io/badge/license-MIT-blue) ![status](https://img.shields.io/badge/status-experiment-lightgrey)

Experiment: Claude Code as the boss, local open-model [pi](https://pi.dev) workers (Ollama,
orchestrated by OpenRig) doing the bounded work it hands over.

**Result so far: on a 32 GB laptop, for small bounded tasks, delegating loses.**
Claude alone did 8 tasks in 46 s; the best local setup (stateless one-shot `pi -p` on
qwen3-coder) took 573 s for the same 8, passing all of them. Details and caveats in
[docs/findings.md](docs/findings.md). Where delegation might still pay (large bulk output,
unattended batches, offline) is untested.

## What is here

| Path | What |
|---|---|
| `scripts/oneshot.sh` | Run one task in a fresh `pi -p`, judged by your check; bounded, process-group kill, private logs |
| `scripts/delegate.sh` | Send a task to a persistent OpenRig seat; finishes when your `--check` passes |
| `skills/`, `commands/`, `.claude-plugin/` | Claude Code plugin: `delegate-local` skill, `/rig-up` `/rig-down` `/rig-status` (validates; never used for real work) |
| `rigs/workers.yaml` | OpenRig rig: two pi builders on qwen3-coder, one pi thinker on devstral |
| `bench/` | 8 tasks with reference solutions, nonce grader, runners, Claude-alone control |
| `scripts/ollama-up.sh` | `ollama serve` with keep-alive and parallel settings, logging to `runs/` |
| `docs/` | [plan](docs/plan.md), [findings](docs/findings.md), [first smoke test](docs/smoke-results.md) |

## Run it

```
./scripts/ollama-up.sh                      # needs Ollama and the qwen3-coder-32k alias (configs/Modelfile.*)
./bench/selftest.sh                         # graders and references
./bench/run.sh my-run oneshot:qwen3-coder-32k   # one-shot benchmark
./bench/claude-alone.sh my-control          # Claude-alone control (uses your Claude quota)
./tests/test-oneshot.sh; ./tests/test-delegate.sh
```

Limits worth knowing: one 32k-context slot of qwen3-coder is 21 GB, a second slot pushed a
32 GB Mac into swap and wedged Ollama. `bench/run.sh` aborts above 90% swap.

## License

MIT, see [LICENSE](LICENSE).
