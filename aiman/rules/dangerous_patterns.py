"""
Static, offline, deterministic rules for catching well-known destructive
shell command patterns.

Deliberately kept separate from the LLM path: these checks must fire
correctly with zero network access and cannot be talked out of it by
clever prompt phrasing.

Each rule is (name, compiled_regex, human_reason).
"""
import re

_RULES = [
    (
        "rm_root_or_wide_recursive",
        r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*|-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*)\s+(/(\s|$)|/\*|~(\s|/\*|$)|\.\s*$|\.\./)",
        "Recursively force-deletes root, home, or the entire current tree.",
    ),
    (
        "rm_no_preserve_root",
        r"--no-preserve-root",
        "Explicitly disables the safeguard that stops rm from wiping '/'.",
    ),
    (
        "fork_bomb",
        r":\(\)\s*\{\s*:\|\s*:\s*&\s*\}\s*;\s*:",
        "Classic fork bomb — spawns processes exponentially until the system locks up.",
    ),
    (
        "disk_overwrite_dd",
        r"\bdd\s+.*\bof=\s*/dev/(sd|nvme|hd|xvd)",
        "Writes raw bytes directly to a disk device — can destroy all data on it.",
    ),
    (
        "mkfs_on_device",
        r"\bmkfs(\.\w+)?\s+/dev/",
        "Formats a block device, erasing everything on that disk/partition.",
    ),
    (
        "chmod_777_root",
        r"\bchmod\s+-R\s+777\s+/(\s|$)",
        "Recursively makes the entire filesystem world-writable — a serious security hole.",
    ),
    (
        "pipe_remote_to_shell",
        r"(curl|wget)\s+.*\|\s*(sudo\s+)?(bash|sh|zsh)\b",
        "Pipes a remote script straight into a shell — executes unreviewed code with no chance to inspect it first.",
    ),
    (
        "overwrite_shadow_passwd",
        r">\s*/etc/(passwd|shadow)\b",
        "Overwrites the system password/user database.",
    ),
    (
        "chown_root_recursive",
        r"\bchown\s+-R\s+\S+\s+/(\s|$)",
        "Recursively changes ownership of the entire filesystem.",
    ),
    (
        "mv_to_devnull_mass",
        r"\bmv\s+/\*\s+/dev/null",
        "Moves the entire root filesystem into the void.",
    ),
    (
        "history_wipe_and_shred",
        r"\bshred\s+.*-(u|z).*\s+/(\s|$)",
        "Securely shreds the root filesystem, making recovery impossible.",
    ),
]

_COMPILED = [(name, re.compile(pattern, re.IGNORECASE), reason) for name, pattern, reason in _RULES]


def match_dangerous_patterns(command: str):
    """
    Returns a list of (rule_name, reason) for every static rule the
    command matches. Empty list means the static filter found nothing —
    it does NOT mean the command is safe, only that it isn't a *known*
    catastrophic pattern.
    """
    hits = []
    for name, pattern, reason in _COMPILED:
        if pattern.search(command):
            hits.append((name, reason))
    return hits
