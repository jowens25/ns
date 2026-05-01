import typer
import asyncio
from typing import Annotated, Literal

cli = typer.Typer()

status_cli = typer.Typer()

cli.add_typer(status_cli, name="status")

from ns2.utils import ASSETS_DIR

from ns2.ui.main import init_ui
from nicegui import ui as nui

from ns2.api.main import init_dbus_service


@cli.command()
def dbus():
    init_dbus_service()


@cli.command()
def ui(debug_mode: Annotated[str, typer.Argument()] = "production"):

    init_ui()
    nui.run(
        port=8000,
        reload=False,
        storage_secret="your-secret-key",
        title="Novus Configuration Tool",
        favicon=str(ASSETS_DIR / "favicon.png"),
    )
