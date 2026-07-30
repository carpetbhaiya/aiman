# 🚀 `aiman` — Comprehensive Project Context & Architecture Guide

> **Note for AI Assistant / Developer Context:** This document provides a complete overview of the `aiman` codebase, design philosophy, file layout, safety guardrails, and implementation history. Use this context to quickly understand the project and continue development seamlessly.

---

## 📌 1. Project Overview

`aiman` is an intelligent, AI-assisted CLI terminal companion built in Python. It replaces standard Linux `man` pages, translates plain-English descriptions into executable shell commands, and guards system integrity with a multi-layered safety checker.

### Core Motto
**"Guardrails inform, they don't block."**  
The AI provides clear safety warnings, risk levels, and double-confirmations for dangerous operations, but the human user retains ultimate control to execute or copy commands.

---

## 🏗️ 2. Architectural Blueprint

```
                      +-----------------------------+
                      |   User Input (CLI Command)  |
                      +--------------+--------------+
                                     |
                                     v
                       +-------------+-------------+
                       |   aiman/detect.py (Mode)  |
                       +-------------+-------------+
                                     |
           +-------------------------+-------------------------+
           |                         |                         |
           v                         v                         v
  +------------------+      +------------------+      +------------------+
  | aiman explain    |      | aiman gen        |      | aiman check      |
  | (Man replacement)|      | (English -> Shell|      | (Safety Review)  |
  +--------+---------+      +--------+---------+      +--------+---------+
           |                         |                         |
           |                         |  (TF-IDF RAG Context)   |
           |                         v                         |
           |                +------------------+               |
           |                | core/generator.py|               |
           |                +--------+---------+               |
           |                         |                         |
           v                         v                         v
+------------------------------------------------------------------------+
|                      core/safety.py (Guardrails)                        |
|   1. Static Regex Blocklist (rules/dangerous_patterns.py) [Instant]    |
|   2. LLM Safety Reviewer (Anti-Prompt Injection, Opaque Delimiters)   |
+------------------------------------+-----------------------------------+
                                     |
                                     v
+------------------------------------------------------------------------+
|                        ui.py & Rich Renderers                          |
|   - Streamed Markdown output      - Tiered Confirmation Dialogs        |
|   - Clipboard Copy (xclip/wl-copy)- Shell Alias Creation (shlex quote) |
+------------------------------------------------------------------------+
```

---

## ⚙️ 3. Key Design Patterns & Technical Decisions

1. **Protocol-Based LLM Abstraction (`aiman/llm/client.py`)**
   * Uses Python's `typing.Protocol` (`LLMClient`).
   * The codebase never directly imports SDKs in business logic.
   * `OllamaLLMClient` handles live local inference (e.g. `qwen3:14b`).
   * `FakeLLMClient` in `tests/conftest.py` enables fast unit testing without network calls or local GPU dependencies.

2. **Layered Safety Defense (`aiman/core/safety.py` & `aiman/rules/dangerous_patterns.py`)**
   * **Layer 1 (Static Regex):** Hardcoded patterns instantly catch catastrophic commands (`rm -rf /`, fork bombs, raw disk overwrites via `dd`, `chmod 777 /`) with zero network latency and zero risk of model hallucination.
   * **Layer 2 (LLM Reviewer):** Analyzes subtler risks (`git push --force`, system config edits) and provides plain-English explanation.
   * **Anti-Prompt-Injection Boundaries:** Prompts wrap input in strict delimiter tags (`---BEGIN USER INPUT---`) and explicitly instruct the LLM to treat inputs as opaque string data rather than instructions.

3. **Grounded Generation via RAG (`aiman/core/generator.py`)**
   * Uses a local TF-IDF vector index (`build_cache.py`, `build_index.py`) compiled from `tldr-pages`.
   * Pulls relevant man page examples as hints into the LLM system prompt to ensure syntax accuracy and accurate flag suggestions.

4. **Dynamic CLI Routing (`aiman/cli.py` & `aiman/detect.py`)**
   * Accepts both explicit subcommands (`aiman explain tar`, `aiman gen list files`) and natural unquoted CLI invocation (`aiman list all pdf files`).
   * `detect_mode()` uses a fast token-based binary lookup heuristic (`shutil.which`) to route commands effortlessly.

---

## 📂 4. Repository Structure

```
aiman/
├── aiman/
│   ├── __init__.py           # Version definition ("0.1.0")
│   ├── cli.py                # Typer CLI entrypoint & subcommand handlers
│   ├── ui.py                 # Rich UI components, panels, spinners, clipboard logic
│   ├── detect.py            # Input mode detector (explain vs. gen vs. check)
│   ├── config.py            # User configuration (~/.config/aiman/config.json) & history
│   ├── core/
│   │   ├── explainer.py     # Command explanation & streaming logic
│   │   ├── generator.py     # English -> Shell translator (with RAG context)
│   │   └── safety.py        # Safety assessment coordinator
│   ├── llm/
│   │   └── client.py        # Protocol definition & Ollama LLM client wrapper
│   └── rules/
│       └── dangerous_patterns.py # Static regex blocklist for dangerous shell patterns
├── scripts/
│   ├── build_cache.py       # Downloads & parses tldr-pages into JSON cache
│   └── build_index.py       # Builds scikit-learn TF-IDF matrix for RAG
├── tests/
│   ├── conftest.py          # Pytest fixtures & FakeLLMClient double
│   ├── test_detect.py       # Tests for routing logic
│   ├── test_explainer.py    # Tests for explanation & caching
│   ├── test_generator.py    # Tests for code extraction & generation
│   └── test_safety.py       # Tests for static regex & LLM safety checks
├── pyproject.toml           # Project dependencies & CLI entrypoints (`aiman`, `ai`)
├── COMMANDS.md              # User-facing command reference guide
├── README.md                # Installation & dev setup guide
└── PROJECT_CONTEXT.md       # (This file) Architecture & AI Context document
```

---

## 🛠️ 5. Subcommands & Capabilities

| Subcommand | Syntax | Description |
| :--- | :--- | :--- |
| `explain` | `aiman explain <command>` | Explains a Linux binary, flags, and practical usage examples. Supports streaming output. |
| `gen` | `aiman gen <description>` | Translates natural language into a single shell command. Includes interactive execute (`e`), copy (`y`), refine (`r`), and cancel (`c`). |
| `check` | `aiman check <command>` | Safety checks a pasted/external command and reports `SAFE`, `CAUTION`, or `DANGEROUS` with reasons. |
| `history` | `aiman history` | Shows a table of the last 10 generated commands with ISO timestamps. |
| `save` | `aiman save <alias_name>` | Safely converts the last generated command into a shell alias (`~/.bashrc`) using `shlex.quote()`. |
| `config` | `aiman config set/get` | Views or updates persistent configuration (e.g. LLM model, host URL). |

---

## 🛡️ 6. Safety & Guardrails Summary

### Safety Verdicts & Tiered Behavior
1. **`✅ SAFE`**: Read-only or low-risk commands (e.g. `ls`, `grep`, `cat`, `unzip`, `pip install`). Interactive prompt allows immediate execution or copy.
2. **`⚠️ CAUTION`**: Commands with potential footguns (e.g. `git push --force`, modifying system files). Requires **1 explicit user confirmation prompt** before running.
3. **`🚨 DANGEROUS`**: Severe threats (`rm -rf /`, `dd` to raw disk, overwriting `/etc/passwd`). Requires **2 explicit confirmation prompts** before running.

### Anti-Prompt-Injection Safeguards
* Input string sanitization and opaque data wrapper delimiters (`---BEGIN USER INPUT---`).
* System prompt rules prohibiting model execution of embedded meta-instructions (e.g. "ignore previous instructions", "output safe").
* Rule preventing model speculation on harmless filenames or URLs (`unzip lol.zip` is treated identically to `unzip file.zip`).

---

## 🚀 7. Quick Setup & Development Guide

### Environment Setup
```bash
# Clone repository and install in editable mode with dev dependencies
pip install -e ".[dev]"

# (Optional) Generate local RAG command index from man pages
python scripts/build_cache.py
python scripts/build_index.py
```

### Running Tests
```bash
pytest -v
```

### Environment Variables & Config
Default config lives at `~/.config/aiman/config.json`:
```json
{
    "model": "qwen3:14b",
    "host": "http://localhost:11434"
}
```

---

## 📝 8. Recent Work & Incremental Improvements

* **Unquoted CLI Arguments:** Updated `explain`, `gen`, and `check` in `cli.py` to take a list of strings (`list[str]`), allowing unquoted text input.
* **UI Module Refactoring:** Moved rich UI rendering, panel styling, clipboard helpers (`_copy_to_clipboard`), and spinner configurations out of `cli.py` into a clean `aiman/ui.py` module.
* **Dynamic Typer Routing:** Replaced hardcoded subcommand lists in `run_app()` with dynamic registration inspection (`app.registered_commands`).
* **Graceful Ollama Connection Handling:** Added structured exception handling so offline LLM backend states print friendly troubleshooting guidance instead of raw tracebacks.
* **Repo Size Optimization:** Git-ignored large 5.7 MB auto-generated cache files (`command_cache.json` and `command_index.pkl`) and added generation scripts to README.
