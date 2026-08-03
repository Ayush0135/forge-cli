from typer.testing import CliRunner

from forge_cli.cli.app import app

runner = CliRunner()


def test_app_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Forge CLI" in result.stdout


def test_chat_command_help() -> None:
    result = runner.invoke(app, ["chat", "--help"])
    assert result.exit_code == 0
