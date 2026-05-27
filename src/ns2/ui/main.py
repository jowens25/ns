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

#!/usr/bin/env python3
"""This is just a simple authentication example.

Please see the `OAuth2 example at FastAPI <https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/>`_  or
use the great `Authlib package <https://docs.authlib.org/en/v0.13/client/starlette.html#using-fastapi>`_ to implement a classing real authentication system.
Here we just demonstrate the NiceGUI integration.
"""
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from nicegui import app, ui
from ns2.lib.bridge import CheckBridge, SetupBridge

unrestricted_page_routes = {
    "/login",
    "/favicon.ico",
}


async def check_auth():

    if stay_logged_in:
        return
    # print("echeck")
    uid = app.storage.user.get("uid")

    guid = app.storage.general.get("uid")

    if not await CheckBridge("admin"):
        # bridge.cleanup()
        app.storage.user.clear()
        ui.navigate.to("/login")

    if guid and guid != uid:
        app.storage.user.clear()
        ui.navigate.to("/login")


'''
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """This middleware restricts access to all NiceGUI pages.
    It redirects the user to the login page if they are not authenticated."""

    path = request.url.path

    if stay_logged_in:
        return await call_next(request)

    # Allow unrestricted routes
    if path in unrestricted_page_routes:
        return await call_next(request)

    # Allow static assets
    if path.startswith("/_nicegui/") or path.startswith("/static/"):
        return await call_next(request)

    # Get the user's session UID
    uid = app.storage.user.get("uid")
    guid = app.storage.general.get("uid")
    # Validate against the active session
    if guid and guid != uid:
        # Clear invalid session
        # app.storage.user.clear()
        # app.storage.general.clear()
        # app.storage.user["redirect_after_login"] = path
        return RedirectResponse("/login")

    return await call_next(request)
#'''
# def init_ui():
#    freeze_support()

# @ui.page("/")
# @ui.page("/overview")
# @ui.page("/networking")
# @ui.page("/networking/firewall")
# @ui.page("/networking/{interface_name}")
# @ui.page("/logs")
# @ui.page("/logs/{log}")
# @ui.page("/services")
# @ui.page("/snmp")
# @ui.page("/snmp/{version}/{user}")
# @ui.page("/terminal")
# @ui.page("/accounts")
# @ui.page("/accounts/{user}")


async def controlPanel():
    with ui.header().classes("items-center justify-between").classes("bg-dark"):
        ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
            "flat color=white"
        )
        ui.image(str(ASSETS_DIR / "NOVUS_LOGO.svg")).classes("w-48")
        ui.label(f"Welcome {app.storage.general.get("activeUser","error")}!")
        with ui.row():
            date = ui.label().classes("font-bold")

            def update_date():
                date.set_text(datetime.now().astimezone().strftime("%m-%d-%Y %H:%M:%S"))

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
        ).props(
            "flat color=white align=left"
        ).classes("full-width")
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

        def logout_cb():
            ui.navigate.to("/login")
            app.storage.general.clear()

        ui.button(
            "Logout",
            on_click=lambda: logout_cb(),
        ).props(
            "flat color=negative align=left"
        ).classes("full-width")
    # Footer
    with ui.footer().classes("bg-dark"):
        ui.label(version("ns2"))
    ui.sub_pages(
        {
            "/": home_page,
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


@ui.page("/")
async def root():
    print("RUNNING ROOT FUNCTION")
    activeUser = await SetupBridge("admin")
    print("BRIDGE FOR: ", activeUser)
    if not app.storage.user.get("uid"):
        app.storage.user.update({"uid": uuid.uuid4()})
    ui.timer(1.0, check_auth)
    init_colors()
    await controlPanel()


restartable = True
stay_logged_in = True
REUSE_FIXED_BRIDGE = True


def restartablefunc():

    ui.run(
        root,
        port=8000,
        reload=True,
        storage_secret="your-secret-key",
        title="Novus Configuration Tool",
        favicon=str(ASSETS_DIR / "favicon.png"),
    )


if restartable:
    restartablefunc()

else:

    if __name__ == "__main__":
        freeze_support()

        ui.run(
            login_page,
            port=8000,
            reload=False,
            storage_secret="your-secret-key",
            title="Novus Configuration Tool",
            favicon=str(ASSETS_DIR / "favicon.png"),
        )
