
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from forge_cli.cli.chat import run_single_prompt, start_interactive_chat
from forge_cli.core.indexer import RepositoryIndexer

app = typer.Typer(help="Forge CLI - AI Coding Assistant")
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """
    Forge CLI - AI Coding Assistant
    """
    if ctx.invoked_subcommand is not None:
        return

    # If no subcommand is invoked, this will be handled by the wrapper in main.py,
    # but for safety if called directly without arguments:
    pass


@app.command()
def project() -> None:
    """Display repository intelligence summary."""
    indexer = RepositoryIndexer()
    idx = indexer.get_index()
    
    table = Table(title=f"Project Summary: {idx.get('project_name', 'Unknown')}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Root", idx.get("project_root", ""))
    table.add_row("Size", f"{idx.get('total_size_bytes', 0) / 1024 / 1024:.2f} MB")
    table.add_row("Total Files", str(idx.get("total_files", 0)))
    table.add_row("Languages", ", ".join(idx.get("languages", {}).keys()))
    table.add_row("Frameworks", ", ".join(idx.get("frameworks", [])))
    table.add_row("Package Managers", ", ".join(idx.get("package_managers", [])))
    
    console.print(table)


@app.command()
def chat() -> None:
    """Start interactive mode."""
    start_interactive_chat()
