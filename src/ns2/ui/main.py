#!/usr/bin/env python3
import asyncio

from fastapi import Request
from fastapi.responses import RedirectResponse
from importlib.metadata import version
from nicegui import app, ui

from datetime import datetime
from zoneinfo import ZoneInfo

from multiprocessing import freeze_support
from ns2.lib.systemd1 import isActive
from ns2.ui import status_page
from ns2.ui.login import logout_cb, login_page

from ns2.ui.accounts_page import accounts_page

from ns2.ui.networking_page import network_page
from ns2.ui.terminal import terminal_page
from ns2.ui.theme import init_colors
from ns2.ui.snmp_page import snmp_page
from ns2.ui.system_page import LoadSystemUnits, system_page
from ns2.ui.status_page import root_status_page

from ns2.lib.bridge import GetBridge
from ns2.lib.timedate1 import CallListTimezones, CallGetTimezone, CallSetTimezone
from ns2.ui.firewalld_page import LoadFirewalldServiceInfo
from ns2.utils import ASSETS_DIR, log

unrestricted_page_routes = {
    "/login",
    "/favicon.ico",
}


async def bridge_check():
    b = GetBridge()
    if b is None:
        app.storage.general.update({"activeUser": None, "activeId": None})
        ui.navigate.reload()


async def check_auth():

    bid = app.storage.browser.get("id", None)
    if bid is None:
        log.info("bid error")
        ui.navigate.to("/login")

    activeId = app.storage.general.get("activeId", None)
    if activeId is None:
        log.info("active id error")
        ui.navigate.to("/login")

    if activeId != bid:
        ui.navigate.to("/login")

    # print(bid)
    # print(activeId)


#'''
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """This middleware restricts access to all NiceGUI pages.
    It redirects the user to the login page if they are not authenticated."""

    path = request.url.path

    bid = app.storage.browser.get("id")
    activeId = app.storage.general.get("activeId")
    if activeId and bid == activeId:
        return await call_next(request)

    # Allow unrestricted routes
    if path in unrestricted_page_routes:
        # log.info("unrestricted")
        return await call_next(request)

    # Allow static assets
    if path.startswith("/_nicegui/") or path.startswith("/static/"):
        # log.info("static")
        return await call_next(request)

    # log.info(f"end of middleware with {path}")

    # log.info("middleware to login")

    return RedirectResponse("/login")


@ui.refreshable
def dateLabel():
    tz = app.storage.general.get("tz", "UTC")

    tzObj = ZoneInfo(tz)
    ui.label(datetime.now().astimezone(tzObj).strftime("%m-%d-%Y %H:%M:%S")).classes(
        "font-bold"
    )


async def Clock():
    dateLabel()

    async def SetTimeCb(e):
        log.info(f"timezone change -> {e.value}")
        await CallSetTimezone(e.value)
        app.storage.general.update({"tz": e.value})

    tzs = await CallListTimezones()
    current_tz = await CallGetTimezone()
    ui.select(tzs, with_input=True, value=current_tz, on_change=SetTimeCb).props(
        "dense"
    )


@ui.page("/")
@ui.page("/network")
@ui.page("/network/firewall")
@ui.page("/network/{interface_name}")
@ui.page("/snmp")
@ui.page("/terminal")
@ui.page("/accounts")
async def controlPanel():

    current_tz = await CallGetTimezone()

    app.storage.general.update({"tz": current_tz})

    ui.timer(1.0, check_auth)
    ui.timer(2.0, bridge_check)
    ui.timer(1.0, dateLabel.refresh)
    init_colors()
    with ui.header().classes("items-center justify-between").classes("bg-dark"):
        ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
            "flat color=white"
        )
        ui.image(str(ASSETS_DIR / "NOVUS_LOGO.svg")).classes("w-48")
        ui.label(f"Welcome {app.storage.general.get("activeUser","error")}!")
        with ui.row().classes("items-center no-wrap"):
            await Clock()

    with ui.left_drawer(bordered=True).classes("bg-dark") as left_drawer:

        def nav(p):
            ui.navigate.to(p)
            left_drawer.hide()

        ui.separator()
        btnps = "flat color=white align=left"

        ui.button("Status", on_click=lambda: nav("/")).props(btnps).classes("w-full")

        ui.button("System", on_click=lambda: nav("/system")).props(btnps).classes(
            "w-full"
        )
        ui.button("Network", on_click=lambda: nav("/network")).props(btnps).classes(
            "w-full"
        )
        ui.button("SNMP", on_click=lambda: nav("/snmp")).props(btnps).classes("w-full")
        ui.button("Accounts", on_click=lambda: nav("/accounts")).props(btnps).classes(
            "w-full"
        )
        ui.button("Terminal", on_click=lambda: nav("/terminal")).props(btnps).classes(
            "w-full"
        )

        ui.separator()

        ui.button(
            "Logout",
            on_click=logout_cb,
        ).props(
            "flat color=negative align=left"
        ).classes("full-width")
    # Footer
    with ui.footer().classes("bg-dark"):
        ui.label(version("ns2"))

    # widget_page()

    ui.sub_pages(
        {
            "/": root_status_page,
            "/system": system_page,
            "/network": network_page,
            # "/network/firewall": firewall_page,
            # "/network/{interface_name}": interface_page,
            "/snmp": snmp_page,
            "/accounts": accounts_page,
            "/terminal": terminal_page,
        }
    ).classes("w-full")


# controlPanel(root_system_page)
# controlPanel(network_page)
# controlPanel(firewall_page)
# controlPanel(interface_page)
# controlPanel(snmp_page)
# controlPanel(accounts_page)
# controlPanel(terminal_page)


production = True


async def LoadStatic():
    active = await isActive("firewalld.service")
    if active["state"]:
        await LoadFirewalldServiceInfo()
    await LoadSystemUnits()
    app.storage.general.update({"activeUser": None, "activeId": None})


# app.on_startup(LoadStatic)


def main():
    freeze_support()
    log.info("app starting")

    asyncio.run(LoadStatic())

    ui.run(
        port=8000,
        reload=False,
        storage_secret="your-secret-key",
        title="Novus Configuration Tool",
        favicon=str(ASSETS_DIR / "favicon.png"),
    )


if __name__ == "__main__" and production:
    main()
# else:

#     ui.run(
#         port=8000,
#         reload=True,
#         storage_secret="your-secret-key",
#         title="Novus Configuration Tool",
#         favicon=str(ASSETS_DIR / "favicon.png"),
#     )
