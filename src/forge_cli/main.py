import sys
from rich.panel import Panel
from rich.console import Console

from forge_cli.cli.app import app
from forge_cli.cli.chat import run_single_prompt, start_interactive_chat


def main() -> None:
    """Entry point for the CLI."""
    args = sys.argv[1:]

    # Subcommands and standard flags supported by Typer
    commands = [
        cmd.name or cmd.callback.__name__
        for cmd in app.registered_commands
        if cmd.callback is not None
    ] + ["--help", "-h"]

    if len(args) == 0:
        Console().print(
            Panel.fit("[bold cyan]Forge CLI v0.1[/bold cyan]\n[white]AI Coding Assistant[/white]", border_style="cyan")
        )
        start_interactive_chat()
        return

    # If the first argument matches a known command or help flag, let Typer handle it
    if args[0] in commands:
        app()
    else:
        # Treat as a single prompt
        prompt = " ".join(args)
        run_single_prompt(prompt)


if __name__ == "__main__":
    main()
