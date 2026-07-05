# aiman

An AI-assisted `man` page + command generator + safety checker, in one CLI.

```
aiman tar                       # -> explains tar syntax + examples
aiman "list all pdfs modified today"   # -> generates the shell command
aiman "rm -rf / --no-preserve-root"    # -> flags it as dangerous
```

## Why this shape

Three independent jobs (explain / generate / check) that all take "some text"
as input. Rather than build one fuzzy do-everything function, each job is its
own module with its own tests, and a thin `detect.py` decides routing. That
means:

- You can unit test "is this command dangerous" without ever touching the LLM.
- You can swap the LLM provider by editing one file (`llm/client.py`).
- If the auto-detect heuristic is ever wrong, explicit subcommands
  (`aiman explain`, `aiman gen`, `aiman check`) always work and never guess.

## Layout

```
aiman/
├── cli.py              entry point — Typer app, routes to core/*
├── detect.py            heuristic: explain vs generate vs check
├── config.py            API key / model config
├── llm/
│   └── client.py         thin wrapper around the Ollama SDK (mockable)
├── core/
│   ├── explainer.py      syntax + examples for a known command
│   ├── generator.py      plain English -> shell command
│   └── safety.py         malicious/dangerous command detection
└── rules/
    └── dangerous_patterns.py   static, offline, un-bypassable blocklist
tests/
    test_detect.py
    test_safety.py
    test_explainer.py
    test_generator.py
    conftest.py           shared fixtures + fake LLM client
```

## Install (local dev)

```
pip install -e ".[dev]"
# If Ollama is running on Windows and you are in WSL, set:
# export OLLAMA_URL="http://<windows_ip>:11434"

# Generate local offline command caches and TF-IDF search index
python scripts/build_cache.py
python scripts/build_index.py

aiman tar
```

## Run tests

```
pytest -v
```

## Design notes / tradeoffs

- **Safety-check is layered, not LLM-only.** A static regex list catches
  known-catastrophic patterns (`rm -rf /`, fork bombs, `curl | bash`,
  `mkfs`, `chmod -R 777 /`, disk overwrites via `dd`, etc.) with zero
  network calls and zero chance the model talks itself out of flagging
  something. The LLM is only consulted for commands that pass the static
  filter, to catch subtler cases (e.g. `git push --force`, obscure `find
  -exec rm` combos) and to explain *why* something is risky in plain English.
- **Guardrails inform, they don't block.** The LLM wrapper never auto-executes commands.
  All generated commands present an option to execute, copy to clipboard, or refine.
  If a command is flagged as caution or dangerous, it requires tiered explicit user confirmation before running.
- **Auto-detect is intentionally simple.** A "smart" classifier that tries
  to read intent from arbitrary text is a bigger, flakier system than the
  actual product. Simple token heuristic + explicit subcommand override
  gets 90% of the UX with 10% of the complexity/failure surface.
