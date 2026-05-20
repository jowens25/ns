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

from ns2.lib.test_networking import run_test

from ns2.lib.authorization import getPid


@cli.command()
def dbus():
    init_dbus_service()


@cli.command()
def test():
    run_test()


@cli.command()
def call():

    print(
        bridgeCall(
            "com.novus.ns",
            "/com/novus/ns",
            "com.novus.ns.snmp.TestSnmpd",
            [],
        )
    )
