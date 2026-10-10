# Findings from the first runs

## Todo app run (Claude lead + 3 builders + reviewer, ~58 min to first accepted build)

- Result: SwiftUI todo app, 6 tests passing, signed `.app` with a generated icon.
- Claude lead: 144 API calls, 88.6k output tokens, 17.9M cache-read tokens.
  pi seats combined: ~93 calls, ~155k input / ~15k output tokens. opencode not measured.
- Every builder file needed a line-level fix list from the lead before it compiled.
  The final UI was rewritten by the lead.
- Builder reports were unreliable: 3 of 5 had no output; one claimed work not done.
- Reviewer (pi): 8 findings, 0 new actionable, 5 false; it had read the worklog.
- Environment traps found only by the lead: SwiftUI `@State` is a macro with no plugin
  under Command Line Tools only; `swift test` intermittently drops the TestingMacros
  plugin (fixed with `-plugin-path` in Package.swift).
- pi quirks: absolute paths written relative to cwd; edit tool fails, whole-file write
  works; "Stream ended without finish_reason" loops (~15 min lost).

## Local model checks (add(a, b) task through pi)

| Model | Result |
|---|---|
| qwen3-coder-32k | pass, 23 s |
| devstral-32k | pass, 60 s incl. load (needs `reasoning: false` in pi models.json) |
| deepseek-r1-32k | fail: no tool calls, invented output |

## Delegation loop (slugify, ~15 lines, to builders-pi-1)

- Seat stopped after three tool calls without writing files; one nudge fixed it.
- It never wrote the requested report file. Code was correct.
- Cost far exceeded doing it directly, which the skill already says for tasks under ~15 lines.
- Led to `--check` (done when the boss's command passes) and a bounded check runtime.

## Machine

- Fan noise during idle: WindowServer at ~91% GPU, not Ollama (idle, 0% GPU).

## Benchmark: 8 bounded Python tasks (bench/), qwen3-coder-32k unless noted

Graded by bench/grade.sh against the original check with a per-run nonce (the first runs
were graded by a check the worker had overwritten; those results were discarded).

| Mode | Passed | Total s | Median s | Notes |
|---|---|---|---|---|
| One-shot `pi -p` per task, qwen3-coder | 8/8 | 573 | 54 | t8 (evaluator) 225 s |
| One-shot, devstral-small-2 | 6/8 | n/a | ~90 | t2 wrote no file, t8 timed out |
| Persistent pi seat, qwen3-coder | 6/8 | 457 + 2 timeouts | 57 | t7, t8 timed out; context drift |
| 2 one-shot streams, 2 Ollama slots | 3/3 done, stopped | 76-102 per task | | model grew 21 -> 25 GB, swap 95% |

- Persistent seats drift: after several tasks the seat re-ran old tasks' tests instead of
  the new one. Stateless one-shot runs do not carry context.
- A Mac that idles to sleep mid-run stalled two runs for ~8.5 min each; the runner now
  uses `caffeinate`.
- Memory is the binding constraint. One 32k-context slot of qwen3-coder is 21 GB; a second
  slot made it 25 GB and swap hit 95%, which wedged Ollama's runner (`Stopping...`) and
  made every later run time out. The runner aborts above 90% swap.
- Prompt style matters: a terse prompt with a relative path made the model print its tool
  call as text (missing `<tool_call>`), 3 of 3; prompts with an absolute path and `cd` worked.
- Parallel slots do not help on this machine at 32k context.

## Control: the same 8 tasks done by Claude alone (headless, claude-sonnet-5-5)

| | Claude alone | One-shot qwen3-coder (local) |
|---|---|---|
| Passed | 8/8 | 8/8 |
| Total time | 46 s (4-10 s per task) | 573 s (32-225 s per task) |
| Claude output tokens | 5,264 total (364-1,324 per task) | 0 (plus the brief the boss writes) |
| Claude cache tokens | 32.8k created, 254.9k read | n/a |
| Notional API cost | $0.21 total | $0 |

- At this size delegation loses on time by ~12x and saves at most ~5k Claude output tokens
  (about $0.2 notional) per 8 tasks, before counting the brief the boss writes and the
  verification it does. The brief (~100-200 tokens) is a sizeable fraction of the answer
  (350-1,300 tokens) it replaces.
- Delegation can only pay when the output is large (hundreds of lines, many files), when
  the work is bulk and can run unattended, or when Claude quota rather than latency is the
  constraint. The break-even task size is not measured yet.
- Caveats: one run per cell; small, well-specified Python tasks; notional cost is Claude's
  own `total_cost_usd`, not what a Pro plan is charged.
