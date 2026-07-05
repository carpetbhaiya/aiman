from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Confirm, Prompt
from rich.spinner import SPINNERS
from rich.live import Live
import subprocess
import random

from aiman.detect import detect_mode
from aiman.llm.client import get_default_client
from aiman.core.explainer import explain_command, explain_command_stream
from aiman.core.generator import generate_command
from aiman.core.safety import assess_command
from aiman.config import load_config, save_config, append_history, get_history

app = typer.Typer(
    add_completion=False, 
    rich_markup_mode="rich",
    help="✨ [bold cyan]AI man page, command generator, and safety checker.[/bold cyan]"
)
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
    
    console.print(f"[bold cyan]Asking AI to explain '{command}'...[/bold cyan]")
    text = ""
    with Live(Panel(Markdown(text), title=f"📘 aiman explain: {command}", border_style="cyan"), refresh_per_second=10) as live:
        for chunk in explain_command_stream(command, llm):
            text += chunk
            live.update(Panel(Markdown(text), title=f"📘 aiman explain: {command}", border_style="cyan"))

def _print_self_capabilities():
    import pyfiglet
    from rich.text import Text
    from rich.align import Align
    
    ascii_art = pyfiglet.figlet_format("AIMAN", font="slant")
    # A beautiful gradient-like feel using rich styles
    banner = Text(ascii_art, style="bold bright_cyan")
    console.print(Align.center(banner))
    
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
    
    current_desc = description
    original_desc = description
    
    while True:
        with console.status("[bold green]Generating command...[/bold green]", spinner=random.choice(RANDOM_SPINNERS)):
            result = generate_command(current_desc, llm)
            
        if "ERROR: Not a Linux command" in result["raw_response"]:
            console.print("[bold red]❌ Request Rejected:[/bold red] I can only help with generating Linux shell commands!")
            raise typer.Exit(1)
            
        md = Markdown(result["raw_response"])
        console.print(Panel(md, title="✨ aiman gen", border_style="green"))
        
        if result["safety"] is not None:
            _print_safety(result["safety"])
        else:
            console.print("[bold yellow]No valid shell command could be extracted from the AI's response.[/bold yellow]")
        
        cmd = result.get("extracted_command")
        safety = result.get("safety")
        
        if not cmd or not safety:
            break
            
        # Determine choices based on safety
        choices = ["e", "r", "c"] if safety.verdict == "safe" else ["r", "c"]
        choice_str = "[e]xecute, [r]efine, [c]ancel" if safety.verdict == "safe" else "[r]efine, [c]ancel (Command is NOT safe)"
        
        if safety.verdict == "safe":
            append_history(original_desc, cmd)
            
        choice = Prompt.ask(f"\n[bold cyan]{choice_str}[/bold cyan]", choices=choices, default="c", show_choices=False)
        
        if choice == "e":
            console.print(f"[dim]Executing: {cmd}[/dim]\n")
            subprocess.run(cmd, shell=True)
            break
        elif choice == "r":
            refinement = Prompt.ask("[bold yellow]How should I change it?[/bold yellow]")
            current_desc = (
                f"Original request: {original_desc}\n"
                f"Previous command generated: `{cmd}`\n"
                f"User's requested change: {refinement}\n"
                f"Generate a new command based on this change."
            )
            console.print() # Add newline before next generation
            continue
        else:
            console.print("[dim]Cancelled.[/dim]")
            break


@app.command()
def check(command: str = typer.Argument(..., help="A shell command to safety-check")):
    """Check whether a pasted command is dangerous before you run it."""
    llm = get_default_client()
    with console.status(f"[bold yellow]Analyzing command safety...[/bold yellow]", spinner=random.choice(RANDOM_SPINNERS)):
        result = assess_command(command, llm)
    _print_safety(result)

@app.command()
def history():
    """View recently generated safe commands."""
    from rich.table import Table
    hist = get_history()
    if not hist:
        console.print("[yellow]No command history found.[/yellow]")
        return
        
    table = Table(title="Recent Commands", border_style="blue")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")
    table.add_column("Command", style="green")
    
    # Show last 10
    recent = hist[-10:]
    for idx, item in enumerate(recent, 1):
        table.add_row(str(idx), item["description"], item["command"])
        
    console.print(table)

@app.command()
def save(alias: str = typer.Argument(..., help="Name of the alias")):
    """Save the last generated safe command as a bash alias."""
    import os
    
    hist = get_history()
    if not hist:
        console.print("[bold red]Error:[/bold red] No history to save.")
        raise typer.Exit(1)
        
    last_cmd = hist[-1]["command"]
    bashrc_path = os.path.expanduser("~/.bashrc")
    
    alias_line = f"\nalias {alias}='{last_cmd}'\n"
    
    try:
        with open(bashrc_path, "a") as f:
            f.write(alias_line)
        console.print(f"[bold green]Success:[/bold green] Saved alias '{alias}' -> '{last_cmd}' in ~/.bashrc")
        console.print("[dim]Run 'source ~/.bashrc' or restart your terminal to use it.[/dim]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Could not write to ~/.bashrc: {e}")



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
    if len(sys.argv) > 1 and sys.argv[1] not in ["explain", "gen", "check", "config", "history", "save", "--help", "-h"]:
        # The user provided free-form text without a subcommand.
        text = " ".join(sys.argv[1:])
        
        # Easter egg
        if text.strip().lower() in ["ai man", "iron man"]:
            console.print("[bold yellow]🤖 Did you mean 'aiman'? I am not Iron Man, I am aiman! But here is what I can do...[/bold yellow]\n")
            text = "aiman"
            
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
