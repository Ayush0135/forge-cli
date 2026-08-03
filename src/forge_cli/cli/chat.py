import sys

from rich.console import Console
from rich.prompt import Prompt

from forge_cli.core.session import Session
from forge_cli.utils.logger import logger

console = Console()


def start_interactive_chat() -> None:
    """Run the interactive chat loop."""
    try:
        session = Session()
        console.print(f"[dim]Started session: {session.session_id}[/dim]")

        # Load previous history if any
        history = session.get_context()
        if history:
            console.print("[dim]Loaded previous conversation history.[/dim]")

        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

                if user_input.strip() == "":
                    continue

                if user_input.strip().lower() in ["/exit", "/quit"]:
                    console.print("[dim]Goodbye![/dim]")
                    break
                elif user_input.strip().lower() == "/clear":
                    session = Session()
                    console.print("[dim]Started new session.[/dim]")
                    continue
                elif user_input.strip().lower() == "/help":
                    console.print("[yellow]Commands:[/yellow] /help, /exit, /clear")
                    continue

                session.add_user_message(user_input)

                console.print("\n[bold magenta]Forge:[/bold magenta] ", end="")

                context = session.get_context()
                original_len = len(context)

                try:
                    for chunk in session.agent.stream_run(context):
                        console.print(chunk, end="", markup=False)
                    console.print()
                except Exception as e:
                    console.print(f"\n[bold red]Error during stream:[/bold red] {e}")
                    continue

                # Save any new messages added by the agent to session memory
                for new_msg in context[original_len:]:
                    session.add_message(new_msg)

            except KeyboardInterrupt:
                console.print("\n[dim]Use /exit to quit.[/dim]")

    except ValueError as e:
        logger.error(str(e))
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


def run_single_prompt(prompt: str) -> None:
    """Run a single prompt and exit."""
    try:
        session = Session()
        session.add_user_message(prompt)

        console.print(f"[bold cyan]You:[/bold cyan] {prompt}\n")
        console.print("[bold magenta]Forge:[/bold magenta] ", end="")

        context = session.get_context()
        original_len = len(context)

        for chunk in session.agent.stream_run(context):
            console.print(chunk, end="", markup=False)
        console.print()

        for new_msg in context[original_len:]:
            session.add_message(new_msg)

    except ValueError as e:
        logger.error(str(e))
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
