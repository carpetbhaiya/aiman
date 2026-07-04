from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Confirm
from rich.spinner import SPINNERS
import subprocess
import random

from aiman.detect import detect_mode
from aiman.llm.client import get_default_client
from aiman.core.explainer import explain_command
from aiman.core.generator import generate_command
from aiman.core.safety import assess_command
from aiman.config import load_config, save_config

app = typer.Typer(add_completion=False, help="AI man page, command generator, and safety checker.")
console = Console()

SPINNERS["pacman"] = {
    "interval": 150,
    "frames": [
        "ᗧ • • •",
        " ᗧ • • ",
        "  ᗧ •  ",
        "   ᗧ   ",
        "   ᗤ   ",
        "  ᗤ •  ",
        " ᗤ • • ",
        "ᗤ • • •"
    ]
}

RANDOM_SPINNERS = [
    "dots", "bouncingBar", "point", "shark", "earth", 
    "moon", "runner", "star", "clock", "pacman"
]

_VERDICT_STYLE = {"safe": "green", "caution": "yellow", "dangerous": "bold red"}

config_app = typer.Typer(help="Manage aiman configuration (e.g., model, host).")
app.add_typer(config_app, name="config")

@config_app.command("set")
def config_set(key: str = typer.Argument(..., help="Config key (model, host)"), value: str = typer.Argument(..., help="New value")):
    valid_keys = ["model", "host"]
    if key not in valid_keys:
        console.print(f"[bold red]Error:[/bold red] Invalid key '{key}'. Valid keys are: {', '.join(valid_keys)}")
        raise typer.Exit(1)
        
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    console.print(f"[bold green]Success:[/bold green] Set {key} to '{value}'")

@config_app.command("get")
def config_get(key: str = typer.Argument(None, help="Config key to view (model, host)")):
    cfg = load_config()
    if key:
        if key not in cfg:
            console.print(f"[bold red]Error:[/bold red] Key '{key}' not found.")
            raise typer.Exit(1)
        console.print(f"{key}: {cfg[key]}")
    else:
        for k, v in cfg.items():
            console.print(f"[bold cyan]{k}:[/bold cyan] {v}")



@app.command()
def explain(command: str = typer.Argument(..., help="Command or utility name, e.g. 'tar'")):
    """Show syntax and examples for a known command."""
    if command.strip().lower() == "aiman":
        _print_self_capabilities()
        raise typer.Exit()
        
    llm = get_default_client()
    with console.status(f"[bold cyan]Asking AI to explain '{command}'...[/bold cyan]", spinner=random.choice(RANDOM_SPINNERS)):
        result = explain_command(command, llm)
    
    md = Markdown(result)
    console.print(Panel(md, title=f"📘 aiman explain: {command}", border_style="cyan"))

def _print_self_capabilities():
    content = """
# 🚀 aiman: Your AI-Powered Terminal Assistant

`aiman` is an intelligent CLI tool that replaces standard `man` pages, generates safe commands from plain English, and protects your system from dangerous mistakes.

## 🛠️ Core Capabilities

*   **Explain Commands:** Just type `aiman <command>` (e.g., `aiman tar`) to get a clear, human-readable explanation with practical examples.
*   **Generate Commands:** Type `aiman "plain english"` (e.g., `aiman "extract this zip file"`) and it will generate the exact shell command you need.
*   **🛡️ Safety Checker:** Every generated or pasted command is run through a strict safety checker. It catches dangerous operations (like `rm -rf /`) before you accidentally execute them.
*   **⚡ Interactive Execution:** If a generated command is marked as `✅ SAFE`, `aiman` will ask if you want to run it instantly.
*   **⚙️ Smart OS Detection:** It knows what OS you're running (e.g., Ubuntu) and automatically adapts its suggestions (like using `apt` instead of `pacman`).
*   **Persistent Config:** Easily switch AI models or server hosts on the fly using `aiman config set model <name>`.

*Built to make the terminal accessible, powerful, and safe.*
"""
    md = Markdown(content.strip())
    console.print(Panel(md, title="✨ aiman capabilities", border_style="magenta"))


@app.command()
def gen(description: str = typer.Argument(..., help="What you want to do, in plain English")):
    """Generate a shell command from a plain-English description."""
    llm = get_default_client()
    with console.status("[bold green]Generating command...[/bold green]", spinner=random.choice(RANDOM_SPINNERS)):
        result = generate_command(description, llm)
        
    md = Markdown(result["raw_response"])
    console.print(Panel(md, title="✨ aiman gen", border_style="green"))
    _print_safety(result["safety"])
    
    cmd = result.get("extracted_command")
    safety = result.get("safety")
    if cmd and safety and safety.verdict == "safe":
        if Confirm.ask("\n[bold cyan]Would you like to execute this command?[/bold cyan]", default=False):
            console.print(f"[dim]Executing: {cmd}[/dim]\n")
            subprocess.run(cmd, shell=True)


@app.command()
def check(command: str = typer.Argument(..., help="A shell command to safety-check")):
    """Check whether a pasted command is dangerous before you run it."""
    llm = get_default_client()
    with console.status(f"[bold yellow]Analyzing command safety...[/bold yellow]", spinner=random.choice(RANDOM_SPINNERS)):
        result = assess_command(command, llm)
    _print_safety(result)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Running `aiman <something>` with no subcommand auto-detects intent.
    For guaranteed behavior, use `aiman explain|gen|check` explicitly.
    """
    if ctx.invoked_subcommand is not None:
        return
    console.print(ctx.get_help())
    raise typer.Exit()


def _print_safety(result) -> None:
    style_map = {
        "safe": ("green", "✅ SAFE"),
        "caution": ("yellow", "⚠️ CAUTION"),
        "dangerous": ("bold red", "🚨 DANGEROUS")
    }
    style, title = style_map.get(result.verdict, ("white", result.verdict.upper()))
    
    reasons = "\n".join(f"• {r}" for r in result.reasons) or "No specific reasons returned."
    
    console.print(Panel(
        f"[{style}]{title}[/{style}]\n\n{reasons}",
        title=f"🛡️  aiman check (source: {result.source})",
        border_style=style.replace("bold ", "")
    ))


def run_app():
    import sys
    from aiman.detect import detect_mode
    
    # Typer parsing workaround: if there's an argument but no valid subcommand, route it properly.
    if len(sys.argv) > 1 and sys.argv[1] not in ["explain", "gen", "check", "config", "--help", "-h"]:
        # The user provided free-form text without a subcommand.
        text = " ".join(sys.argv[1:])
        mode = detect_mode(text)
        console.print(f"[dim]auto-detected mode: {mode} (use 'aiman explain/gen/check' to override)[/dim]")
        if mode == "explain":
            sys.argv = [sys.argv[0], "explain", text]
        elif mode == "generate":
            sys.argv = [sys.argv[0], "gen", text]
        else:
            sys.argv = [sys.argv[0], "check", text]
            
    app()

if __name__ == "__main__":
    run_app()
