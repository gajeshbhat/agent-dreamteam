# Dreamteam plan

Status 2026-10-10: built and measured; not worth it at small task sizes (see Outcome).

## Shape

A Claude Code session is the boss. A rig of local open-model pi workers (Ollama, via
OpenRig) does bounded work it hands over. A Claude Code plugin (this repo) decides when,
sends the task, and verifies the result itself.

| Piece | What |
|---|---|
| Boss | The Claude Code session you work in, attached to the rig as `builders.boss` |
| Workers | `builders-pi-1`, `builders-pi-2`: pi on `qwen3-coder-32k` (qwen3-coder:30b, 32k ctx) |
| Thinker | `thinker-pi`: pi on `devstral-32k` (devstral-small-2:24b, 32k ctx) |
| Plugin | skill `delegate-local`, commands `/rig-up` `/rig-down` `/rig-status`, `scripts/delegate.sh` |
| Telemetry | `scripts/telemetry.sh` (rig, Ollama, memory samples) and `runs/delegations.jsonl` |

Machine: MacBook Pro M4, 32 GB. One large model fits at a time (21 GB loaded for the 30B),
so the thinker swaps in on demand.

`rigs/dreamteam.yaml` is the earlier layout with a Claude lead seat and an opencode seat;
kept for history. `rigs/workers.yaml` is the current rig.

## Decisions so far

- opencode dropped: no model flag on its TUI, picked up stale state, hung once.
- Codex and auggie dropped: open models everywhere except the boss.
- DeepSeek R1 14B rejected as a worker: no tool calls through pi, invented a result.
- Completion is proven by a command the boss runs (`--check`), not by a worker report.
- iii deferred until the rig is proven; see below.

## Outcome

The benchmark (see [findings.md](findings.md)) showed that for small bounded tasks Claude alone
is about 12 times faster and the local workers add no accuracy, so automatic delegation is not
worth it at this scale. Stateless one-shot runs beat persistent seats. Parallel slots do not fit
in 32 GB at 32k context.

## If this is picked up again

1. Measure the break-even: bulk tasks (20+ functions or a 300-500 line module) against the
   Claude-alone control. Only there can delegation win.
2. Token accounting per delegation (pi session usage plus the boss's usage delta).
3. One automatic retry in `oneshot.sh` when the model prints a tool call as text.
4. `rig mcp serve` tools in the boss session (wired, never loaded).
5. iii: a shared task queue that seats pull from. Only if 1 shows delegation is worth having.
