"""Interface for ``python -m hive_controller_ioc`` using Typer."""

import logging

import typer

from ._version import __version__
from .ioc import start_ioc

app = typer.Typer(no_args_is_help=True)


@app.command()
def run(
    host: str = typer.Argument(..., help="The IP of the target hive controller"),
    prefix: str = typer.Argument(..., help="The EPICS prefix for the hive controller"),
    bob_dir: str = typer.Option(..., help="The directory of the bobfile"),
    logging_level: str = typer.Option("error", help="The logging level"),
):
    """
    Start the IOC.

    ARGS:
        host: The IP of the target hive controller.
        prefix: The EPICS prefix for the hive controller.
    """
    typer.echo("IOC starting...")
    setup_logging(logging_level)
    start_ioc(host, prefix, bob_dir)


def setup_logging(logging_level: str):
    """
    Sets up the logging level based on the CLI param
    """
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    level = level_map.get(logging_level.lower(), logging.ERROR)
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    )

    logging.debug("Logging is set up.")


def version_callback(value: bool):
    if value:
        typer.echo(f"Hive-Controller-IOC Version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(version: bool = typer.Option(None, "--version", callback=version_callback)):
    """
    IOC entry point
    """


if __name__ == "__main__":
    app()
