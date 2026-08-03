from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from forge_cli.cli.chat import run_single_prompt, start_interactive_chat

app = typer.Typer(help="Forge CLI - AI Coding Assistant")
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context, prompt: Optional[str] = typer.Argument(None, help="Optional single prompt to run")
) -> None:
    """
    Forge CLI - AI Coding Assistant
    """
    if ctx.invoked_subcommand is not None:
        return

    if prompt:
        run_single_prompt(prompt)
    else:
        console.print(
            Panel.fit("[bold cyan]Forge CLI v0.1[/bold cyan]\n[white]AI Coding Assistant[/white]", border_style="cyan")
        )
        start_interactive_chat()


@app.command()
def chat() -> None:
    """Start interactive mode."""
    start_interactive_chat()
