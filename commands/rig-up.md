---
description: Start the local open-model worker rig and attach this session as the boss
allowed-tools: Bash
---
Run `${CLAUDE_PLUGIN_ROOT}/scripts/rig-up.sh` and report the seat list. Ollama must already be serving (check `curl -s 127.0.0.1:11434/api/version`); if it is not, say so and stop.
