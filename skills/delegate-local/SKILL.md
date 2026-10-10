---
name: delegate-local
description: Use when a coding task is bounded, well specified and verifiable (bulk or repetitive edits, writing tests for existing code, summarising or scanning many files, drafting a self-contained file) and the local worker rig is running, to hand it to a local open-model pi seat and save Claude tokens or time. Not for design, hard debugging, or anything small enough to do directly.
---

# Delegate to local workers

Workers are pi seats on Ollama (`builders-pi-1@workers`, `builders-pi-2@workers`; `thinker-pi@workers` runs devstral-small-2 for plans and reviews). Check `rig ps --nodes --rig workers`; if the rig is not up, do the work yourself or tell the user to run `/rig-up`. Never start the rig on your own.

## Delegate when ALL hold
- The task fits in a few sentences and names exact files by absolute path.
- Success is checkable by a command you can run yourself (build, test, grep, diff).
- It is more than about 15 lines of output, or many files, or parallelisable across two seats.

## Do it yourself when ANY holds
- Design, API shape, or a decision with trade-offs.
- Debugging an unknown cause, or anything involving the toolchain or environment.
- Under about 15 lines, or one quick edit: writing the brief costs more than the work.

## How
1. Write the task with exact files, the contract, and the check command. Splitting across seats: separate files per seat, never the same file.
2. Run `${CLAUDE_PLUGIN_ROOT}/scripts/delegate.sh <seat@workers> "<task>" --check "<command that passes only when the work is right>" --timeout 600`. It stamps your identity, adds the rules below, and finishes as soon as your check passes or the worker writes a report; logs to `runs/delegations.jsonl`. Always pass `--check`: local workers often ignore the report-file instruction (seen twice) and sometimes stop after a tool call and need one nudge.
3. Verify yourself. A report is a claim, not evidence. Re-run the check in an isolated build path (`swift build --scratch-path <tmp>`), read the diff, check mtimes. `NO EVIDENCE` on stderr means the report had no command output.
4. If a worker output needs more than one fix round, take the file over yourself.

## What went wrong in the first run (assume it will again)
- Workers wrote to the wrong directory: absolute path plus explicit `cd` in every task.
- Edit tool failures in pi: ask for whole-file writes.
- Self-reports without output, or for work not done: always verify.
- Two seats building in one `.build` broke tests: use `--scratch-path`.
- Local models drafted code that needed line-level fix lists; this is only worth it for bulk or parallel work.

DeepSeek R1 14B is not a worker: through pi it made no tool calls and invented a result. Use `ollama run deepseek-r1-32k` directly for tool-free reasoning on text you paste in.

Do not tell workers secrets or paste credentials into tasks.
