#!/usr/bin/env python3
from importlib.metadata import version
from nicegui import app, ui


from datetime import datetime

from multiprocessing import freeze_support
from ns2.ui.login import login_page, logout_cb

from ns2.ui.logs_page import logs_page, log_page
from ns2.ui.accounts_page import accounts_page, accounts_user_page

from ns2.ui.networking_page import network_page, interface_page
from ns2.ui.terminal import terminal_page
from ns2.ui.theme import init_colors
from ns2.ui.home_page import home_page
from ns2.ui.snmp_page import snmp_page, snmp_user_page
from ns2.ui.services_page import services_page


from ns2.ui.firewalld_page import firewall_page
from ns2.utils import ASSETS_DIR, log


from fastapi import Request
from fastapi.responses import RedirectResponse

unrestricted_page_routes = {
    "/",
    "/favicon.ico",
}


async def check_auth():

    log.info("auth check")
    uid = app.storage.user.get("uid", None)
    guid = app.storage.general.get("uid", None)

    if guid and guid != uid:
        app.storage.user.clear()
        ui.navigate.to("/")


#'''
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """This middleware restricts access to all NiceGUI pages.
    It redirects the user to the login page if they are not authenticated."""

    path = request.url.path

    log.info(path)

    # if stay_logged_in:
    #    return await call_next(request)

    # Allow unrestricted routes
    if path in unrestricted_page_routes:
        log.info("unrestricted")
        return await call_next(request)

    # Allow static assets
    if path.startswith("/_nicegui/") or path.startswith("/static/"):
        log.info("static")
        return await call_next(request)

    # Get the user's session UID
    uid = app.storage.user.get("uid")
    guid = app.storage.general.get("uid")
    # Validate against the active session
    if guid and guid != uid:
        # Clear invalid session
        app.storage.user.clear()
        app.storage.general.clear()
        # app.storage.user["redirect_after_login"] = path
        log.info("/login")
        return RedirectResponse("/login")

    return await call_next(request)


@ui.page("/home")
def controlPanel():
    init_colors()
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
            on_click=lambda: ui.navigate.to("/home"),
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
            "/home": home_page,
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


if __name__ == "__main__":
    freeze_support()
    log.info("app starting")
    ui.run(
        login_page,
        port=8000,
        reload=False,
        storage_secret="your-secret-key",
        title="Novus Configuration Tool",
        favicon=str(ASSETS_DIR / "favicon.png"),
    )
