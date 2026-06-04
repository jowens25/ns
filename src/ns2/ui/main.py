#!/usr/bin/env python3
from fastapi import Request
from fastapi.responses import RedirectResponse
from importlib.metadata import version
from nicegui import app, ui

from datetime import datetime
from zoneinfo import ZoneInfo

from multiprocessing import freeze_support
from ns2.ui.login import logout_cb

from ns2.ui.accounts_page import accounts_page

from ns2.ui.networking_page import network_page, interface_page
from ns2.ui.terminal import terminal_page
from ns2.ui.theme import init_colors
from ns2.ui.home_page import home_page
from ns2.ui.snmp_page import snmp_page
from ns2.ui.system_page import root_system_page

from ns2.lib.timedate1 import CallListTimezones, CallGetTimezone, CallSetTimezone
from ns2.ui.firewalld_page import firewall_page
from ns2.utils import ASSETS_DIR, log

unrestricted_page_routes = {
    "/login",
    "/favicon.ico",
}


async def check_auth():

    # log.info("auth check")
    uid = app.storage.user.get("uid", None)
    guid = app.storage.general.get("uid", None)

    if guid and guid != uid:
        app.storage.general.clear()
        log.info("check auth: general store cleared")
        ui.navigate.to("/")
    elif guid is None and uid is None:
        log.info("loggd out????")

    # log.info(f"uid: {uid}")
    # log.info(f"guid: {guid}")


#'''
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """This middleware restricts access to all NiceGUI pages.
    It redirects the user to the login page if they are not authenticated."""

    path = request.url.path

    # log.info(path)

    uid = app.storage.user.get("uid")
    guid = app.storage.general.get("uid")
    if guid and uid == guid:
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
@ui.page("/networking")
@ui.page("/networking/firewall")
@ui.page("/networking/{interface_name}")
@ui.page("/logs")
@ui.page("/logs/{log}")
@ui.page("/services")
@ui.page("/snmp")
@ui.page("/terminal")
@ui.page("/accounts")
@ui.page("/accounts/{user}")
async def controlPanel():

    current_tz = await CallGetTimezone()

    app.storage.general.update({"tz": current_tz})

    ui.timer(1.0, check_auth)
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
        ui.separator()
        ui.button(
            "System",
            on_click=lambda: ui.navigate.to("/"),
        ).props(
            "flat color=white align=left"
        ).classes("full-width")
        ui.button(
            "Networking",
            on_click=lambda: ui.navigate.to("/networking"),
        ).props(
            "flat color=white align=left"
        ).classes("full-width")
        # ui.button(
        #    "Logs",
        #    on_click=lambda: ui.navigate.to("/logs"),
        # ).props(
        #    "flat color=white align=left"
        # ).classes("full-width")
        # ui.button(
        #    "Services",
        #    on_click=lambda: ui.navigate.to("/services"),
        # ).props(
        #    "flat color=white align=left"
        # ).classes("full-width")
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
            on_click=logout_cb,
        ).props(
            "flat color=negative align=left"
        ).classes("full-width")
    # Footer
    with ui.footer().classes("bg-dark"):
        ui.label(version("ns2"))
    ui.sub_pages(
        {
            "/": root_system_page,
            "/networking": network_page,
            "/networking/firewall": firewall_page,
            "/networking/{interface_name}": interface_page,
            # "/logs": logs_page,
            # "/logs/{log}": log_page,
            "/snmp": snmp_page,
            "/accounts": accounts_page,
            "/terminal": terminal_page,
            #'/tests': tests_page
        }
    ).classes("w-full")


production = False


def main():
    freeze_support()
    log.info("app starting")

    ui.run(
        port=8000,
        reload=False,
        storage_secret="your-secret-key",
        title="Novus Configuration Tool",
        favicon=str(ASSETS_DIR / "favicon.png"),
    )


if __name__ == "__main__" and production:
    main()
else:

    ui.run(
        port=8000,
        reload=True,
        storage_secret="your-secret-key",
        title="Novus Configuration Tool",
        favicon=str(ASSETS_DIR / "favicon.png"),
    )
