import json
import subprocess


class ShellTools:
    """Secure shell execution tools."""

    @staticmethod
    def run_command(command: str, cwd: str | None = None) -> str:
        """Executes a shell command and returns structured JSON output."""
        try:
            # We use shell=True for convenience but we must be careful with interactive commands.
            # Timeout prevents hanging the agent forever.
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
                timeout=120  # 2 minute timeout
            )
            return json.dumps(
                {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode,
                }
            )
        except subprocess.TimeoutExpired:
            return json.dumps(
                {
                    "stdout": "",
                    "stderr": f"Command '{command}' timed out after 120 seconds.",
                    "exit_code": 124,
                }
            )
        except (OSError, ValueError) as e:
            return json.dumps(
                {
                    "stdout": "",
                    "stderr": f"Exception executing command: {e!s}",
                    "exit_code": 1,
                }
            )
