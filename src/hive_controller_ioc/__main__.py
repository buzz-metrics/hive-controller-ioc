"""Interface for ``python -m hive_controller_ioc`` using Typer."""

import typer

from ._version import __version__
from .ioc import start_ioc

app = typer.Typer(no_args_is_help=True)


@app.command()
def run(
    host: str = typer.Argument(..., help="The IP of the target hive controller"),
    prefix: str = typer.Argument(..., help="The EPICS prefix for the hive controller"),
):
    """
    Start the IOC.

    ARGS:
        host: The IP of the target hive controller.
        prefix: The EPICS prefix for the hive controller.
    """
    if not (host and prefix):
        typer.echo("Please provide a host and a prefix")
        raise typer.Exit(code=1)

    typer.echo("Things are happening")
    start_ioc(host, prefix)


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
