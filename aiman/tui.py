from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Markdown, RichLog
from textual.containers import Vertical
from textual import work
from textual.binding import Binding

import subprocess

from aiman.llm.client import get_default_client
from aiman.core.generator import generate_command

class AimanTUI(App):
    """A Textual app for interacting with Aiman."""
    
    CSS = """
    #chat-container {
        height: 1fr;
    }
    #chat-log {
        height: 1fr;
        padding: 1 2;
        border: solid green;
    }
    #input {
        dock: bottom;
        margin: 1;
    }
    #exec-log {
        height: 10;
        border: solid yellow;
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding("ctrl+e", "execute_command", "Execute Safe Command", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.llm = get_default_client()
        self.last_generated_command = None
        self.chat_history = "# 🚀 Welcome to aiman chat!\n\nType what you want to do below.\n"

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="chat-container"):
            yield Markdown(self.chat_history, id="chat-log")
        yield RichLog(id="exec-log", highlight=True, markup=True)
        yield Input(placeholder="Ask for a Linux command...", id="input")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()
        log = self.query_one(RichLog)
        log.write("[dim]Execution output will appear here.[/dim]")

    @work(thread=True)
    def fetch_command(self, query: str) -> None:
        try:
            result = generate_command(query, self.llm)
            self.app.call_from_thread(self.handle_ai_response, query, result)
        except Exception as e:
            self.app.call_from_thread(self.append_error, query, str(e))

    def handle_ai_response(self, query: str, result: dict) -> None:
        raw = result.get("raw_response", "")
        cmd = result.get("extracted_command")
        safety = result.get("safety")

        self.chat_history += f"\n---\n**You:** {query}\n\n**Aiman:**\n{raw}\n"
        
        if safety:
            if safety.verdict == "safe":
                self.chat_history += f"\n> ✅ **SAFE**: {safety.reasons[0] if safety.reasons else 'No reasons.'}\n> Press `Ctrl+E` to execute this command.\n"
                self.last_generated_command = cmd
            else:
                self.chat_history += f"\n> 🚨 **DANGEROUS**: {safety.reasons[0] if safety.reasons else 'Unsafe.'}\n> Execution disabled.\n"
                self.last_generated_command = None

        md_widget = self.query_one("#chat-log", Markdown)
        md_widget.update(self.chat_history)
        
        input_widget = self.query_one(Input)
        input_widget.disabled = False
        input_widget.value = ""
        input_widget.focus()

    def append_error(self, query: str, err: str) -> None:
        self.chat_history += f"\n---\n**You:** {query}\n\n**Error:** {err}\n"
        self.query_one("#chat-log", Markdown).update(self.chat_history)
        
        input_widget = self.query_one(Input)
        input_widget.disabled = False
        input_widget.focus()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        query = message.value.strip()
        if not query:
            return
            
        message.input.disabled = True
        self.last_generated_command = None # clear previous command
        
        # Show loading indicator in markdown
        temp_history = self.chat_history + f"\n---\n**You:** {query}\n\n*Generating command...*\n"
        self.query_one("#chat-log", Markdown).update(temp_history)
        
        self.fetch_command(query)

    def action_execute_command(self) -> None:
        if not self.last_generated_command:
            log = self.query_one(RichLog)
            log.write("[bold red]No safe command generated to execute![/bold red]")
            return
            
        cmd = self.last_generated_command
        log = self.query_one(RichLog)
        log.write(f"\n[bold cyan]Executing:[/bold cyan] {cmd}")
        
        # Execute asynchronously so UI doesn't freeze
        self.run_subprocess(cmd)
        
        # Clear it so they don't execute it twice accidentally
        self.last_generated_command = None

    @work(thread=True)
    def run_subprocess(self, cmd: str) -> None:
        try:
            # We use shell=True because the AI generates full bash syntax/pipes
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True
            )
            
            if process.stdout:
                for line in process.stdout:
                    self.app.call_from_thread(self.write_log, line.rstrip())
                
            process.wait()
            if process.returncode == 0:
                self.app.call_from_thread(self.write_log, "[bold green]Process finished successfully.[/bold green]")
            else:
                self.app.call_from_thread(self.write_log, f"[bold red]Process exited with code {process.returncode}.[/bold red]")
        except Exception as e:
            self.app.call_from_thread(self.write_log, f"[bold red]Execution error:[/bold red] {e}")

    def write_log(self, text: str) -> None:
        log = self.query_one(RichLog)
        log.write(text)

def run_tui():
    app = AimanTUI()
    app.run()
