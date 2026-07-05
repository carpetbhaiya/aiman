from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.spinner import SPINNERS
import subprocess

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

def print_self_capabilities() -> None:
    import pyfiglet
    from rich.text import Text
    from rich.align import Align
    
    ascii_art = pyfiglet.figlet_format("AIMAN", font="slant")
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


def print_safety(result) -> None:
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


def copy_to_clipboard(cmd: str) -> None:
    """Copy a command to the system clipboard, with fallbacks."""
    import shutil as _shutil
    
    copied = False
    for tool, args in [
        ("xclip", ["xclip", "-selection", "clipboard"]),
        ("xsel", ["xsel", "--clipboard", "--input"]),
        ("wl-copy", ["wl-copy"]),
    ]:
        if _shutil.which(tool):
            try:
                proc = subprocess.run(args, input=cmd, text=True, capture_output=True, timeout=5)
                if proc.returncode == 0:
                    console.print(f"[bold green]📋 Copied to clipboard![/bold green] [dim]{cmd}[/dim]")
                    copied = True
                    break
            except Exception:
                continue
    
    if not copied:
        console.print(Panel(
            f"[bold]{cmd}[/bold]",
            title="📋 Copy this command",
            border_style="cyan",
            subtitle="[dim]Install xclip or xsel for auto-copy[/dim]"
        ))
