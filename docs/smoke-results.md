# Smoke test: pi and opencode on qwen3-coder

Run 2026-10-10 on an M4 / 32 GB. Model: `qwen3-coder-32k`
(`configs/Modelfile.qwen3-coder-32k`, i.e. `qwen3-coder:30b` with `num_ctx 32768`).

Task, given to each harness in an empty temp directory:

> Create add.py defining add(a, b) that returns a+b, then run
> python3 -c "from add import add; print(add(2,3))" and tell me the output.

Pass means `add.py` exists and `add(2,3) == 5` (checked by me, not by the agent).

| Harness | Result | Wall time | Notes |
|---|---|---|---|
| pi 1.1.0 | pass | 23 s | `pi -p --no-session --provider ollama --model qwen3-coder-32k`. Warned the model was missing from `models.json` and used the id anyway |
| opencode 2.0.26 | pass | ~28 s | `OPENCODE_CONFIG=configs/opencode.json opencode run --standalone --auto -m ollama/qwen3-coder-32k` |

Observations:

- Both made the tool calls correctly (write file, run command) on the first try.
- Loaded model: 21 GB, 100% GPU, context 32768 (`ollama ps`).
- The first opencode attempt hung for 10 minutes with no file written and no model
  loaded. Two later runs (a trivial prompt and the task above) passed and exited on
  their own, so I could not reproduce it. Cause unknown. Keep a timeout on opencode
  runs until it is explained.
- One task per harness is a smoke test, not a benchmark. Tokens/s and parallel
  behaviour are still unmeasured.
