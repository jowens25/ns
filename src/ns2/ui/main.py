#!/usr/bin/env python3
from importlib.metadata import version, PackageNotFoundError
from zoneinfo import ZoneInfo
import asyncio
from ns2.api.dbus import get_dbus, cleanup_dbus, AppBus
from dbus_next.aio import MessageBus
from dbus_next import BusType

from datetime import datetime
import zoneinfo
import sys
from nicegui import ui, app
from multiprocessing import freeze_support

from ns2.ui.logs_page import logs_page, log_page
from ns2.ui.accounts_page import accounts_page, accounts_user_page
from ns2.lib.ns_socket import socket_stream
from ns2.ui.networking_page import network_page, interface_page
from ns2.ui.terminal import terminal_page
from ns2.ui.theme import init_colors
from ns2.ui.login import login_page
from ns2.ui.home_page import home_page
from ns2.ui.snmp_page import snmp_page, snmp_user_page
from ns2.ui.services_page import services_page

# from ns2.ntp import ntp_page
from ns2.ui.fpga_page import fpga_page

# from ns2.tests_page import tests_page
from ns2.ui.firewalld_page import firewall_page
from ns2.utils import ASSETS_DIR

sock_task = None


def init_ui():

    freeze_support()

    @ui.page("/")
    @ui.page("/overview")
    @ui.page("/networking")
    @ui.page("/networking/firewall")
    @ui.page("/networking/{interface_name}")
    @ui.page("/logs")
    @ui.page("/logs/{log}")
    @ui.page("/services")
    @ui.page("/snmp")
    @ui.page("/snmp/{version}/{user}")
    @ui.page("/terminal")
    @ui.page("/accounts")
    @ui.page("/accounts/{user}")
    async def root():
        init_colors()
        if not app.storage.client.get("authenticated", False):
            ui.navigate.to("/login")
            return
        with ui.header().classes("items-center justify-between").classes("bg-dark"):
            ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
                "flat color=white"
            )
            ui.image(str(ASSETS_DIR / "NOVUS_LOGO.svg")).classes("w-48")
            ui.label(f'Welcome {app.storage.client["username"]}!')
            # ui.button("Request Admin").classes("bg-secondary").props("flat color=accent")
            with ui.row():
                # with ui.dialog() as dialog, ui.card():
                #
                #    tz = ui.input(label="Time zone", value="UTC")
                #
                #    # ui.button("Save", on_click=tzDialog.close).props(
                #    #    "flat color=accent dense"
                #    # )
                #
                # ui.button("Change Time Zone", on_click=dialog.open).props(
                #    "flat color=accent dense"
                # )
                label = ui.label().classes("font-bold")

                def update_date():
                    label.set_text(
                        datetime.now().astimezone().strftime("%m-%d-%Y %H:%M:%S")
                    )

            ui.timer(1.0, update_date)

        async def nav(path: str):
            if path == "/login":
                app.storage.client.clear()
                cleanup_dbus()
            ui.navigate.to(path)
            width = await ui.run_javascript("window.innerWidth")
            if width < 1024:  # Adjust this breakpoint as needed
                left_drawer.hide()

        with ui.left_drawer(bordered=True).classes("bg-dark") as left_drawer:
            # ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
            #    "flat color=white"
            # )
            ui.separator()
            ui.button(
                "Overview",
                on_click=lambda: nav("/overview"),
            ).props(
                "flat color=white align=left"
            ).classes("full-width")
            ui.button(
                "Networking",
                on_click=lambda: nav("/networking"),
            ).props(
                "flat color=white align=left"
            ).classes("full-width")
            ui.button(
                "Logs",
                on_click=lambda: nav("/logs"),
            ).props(
                "flat color=white align=left"
            ).classes("full-width")
            ui.button(
                "Services",
                on_click=lambda: nav("/services"),
            ).props(
                "flat color=white align=left"
            ).classes("full-width")
            ui.button(
                "Terminal",
                on_click=lambda: nav("/terminal"),
            ).props(
                "flat color=white align=left"
            ).classes("full-width")
            ui.button(
                "SNMP",
                on_click=lambda: nav("/snmp"),
            ).props(
                "flat color=white align=left"
            ).classes("full-width")
            ui.button(
                "Accounts",
                on_click=lambda: nav("/accounts"),
            ).props(
                "flat color=white align=left"
            ).classes("full-width")
            ui.separator()
            ui.button(
                "Logout",
                on_click=lambda: nav("/login"),
            ).props(
                "flat color=negative align=left"
            ).classes("full-width")
        # Footer
        with ui.footer().classes("bg-dark"):
            ui.label(version("ns2"))
        ui.sub_pages(
            {
                "/": home_page,
                "/overview": home_page,
                "/networking": network_page,
                "/networking/firewall": firewall_page,
                "/networking/{interface_name}": interface_page,
                "/logs": logs_page,
                "/logs/{log}": log_page,
                "/snmp": snmp_page,
                "/snmp/{version}/{user}": snmp_user_page,
                "/accounts": accounts_page,
                "/accounts/{user}": accounts_user_page,
                "/terminal": terminal_page,
                "/services": services_page,
                #'/tests': tests_page
            }
        ).classes("w-full")

    @app.on_startup
    async def startup():
        print("get to dbus??/")
        await get_dbus()

    @app.on_shutdown
    async def shutdown():
        cleanup_dbus()
