import logging

from rich.logging import RichHandler


def setup_logger() -> logging.Logger:
    logging.basicConfig(
        level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True, markup=True)]
    )
    return logging.getLogger("forge_cli")


logger = setup_logger()
