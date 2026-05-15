#!/usr/bin/env python3
from importlib.metadata import version

import uuid

from datetime import datetime

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

app.storage.general.update({"uids": []})


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

        await ui.context.client.connected()
        if not app.storage.tab.get("uid", False):
            initUid = str(uuid.uuid4())
            # print("uuid: ", initUid)
            # when they connect they get an id
            app.storage.tab.update({"uid": initUid})
            # we add that id to our list
            app.storage.general["uids"].append(initUid)

        async def check_active_user():
            await ui.context.client.connected()
            # get the "active" user marked in the auth func
            active_uid = app.storage.general.get("activeUser", None)
            # print("active uid: ", active_uid)
            if active_uid != app.storage.tab.get("uid"):
                ui.navigate.to("/login")
                return

        await check_active_user()
        ui.timer(1.0, lambda: check_active_user)

        with ui.header().classes("items-center justify-between").classes("bg-dark"):
            ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
                "flat color=white"
            )
            ui.image(str(ASSETS_DIR / "NOVUS_LOGO.svg")).classes("w-48")
            ui.label(f"Welcome {app.storage.general.get("username","error")}!")
            with ui.row():
                date = ui.label().classes("font-bold")

                def update_date():
                    date.set_text(
                        datetime.now().astimezone().strftime("%m-%d-%Y %H:%M:%S")
                    )

            ui.timer(1.0, update_date)

        with ui.left_drawer(bordered=True).classes("bg-dark") as left_drawer:
            ui.separator()
            ui.button(
                "Overview",
                on_click=lambda: ui.navigate.to("/overview"),
            ).props(
                "flat color=white align=left"
            ).classes("full-width")
            ui.button(
                "Networking",
                on_click=lambda: ui.navigate.to("/networking"),
            ).props("flat color=white align=left").classes("full-width")
            ui.button(
                "Logs",
                on_click=lambda: ui.navigate.to("/logs"),
            ).props(
                "flat color=white align=left"
            ).classes("full-width")
            ui.button(
                "Services",
                on_click=lambda: ui.navigate.to("/services"),
            ).props(
                "flat color=white align=left"
            ).classes("full-width")
            ui.button(
                "Terminal",
                on_click=lambda: ui.navigate.to("/terminal"),
            ).props(
                "flat color=white align=left"
            ).classes("full-width")
            ui.button(
                "SNMP",
                on_click=lambda: ui.navigate.to("/snmp"),
            ).props(
                "flat color=white align=left"
            ).classes("full-width")
            ui.button(
                "Accounts",
                on_click=lambda: ui.navigate.to("/accounts"),
            ).props(
                "flat color=white align=left"
            ).classes("full-width")
            ui.separator()
            ui.button(
                "Logout",
                on_click=lambda: ui.navigate.to("/login"),
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
