from nicegui import ui, app

from ns2.ui.theme import init_colors
import time
from ns2.utils import ASSETS_DIR
from ns2.api.pam_interface import GetPamInterface
from ns2.api.dbus import get_dbus


async def try_login(_username: str, _password: str) -> None:

    bus = await get_dbus()
    pam = await GetPamInterface(bus)

    if await pam.call_authenticate(_username, _password):
        app.storage.user.update(
            {
                "username": _username,
                "authenticated": True,
                # "token": response["token"],
                "login_time": time.time(),
            }
        )
        ui.notify(f"Welcome, {_username}!", color="positive")
        ui.navigate.to("/overview")
    else:
        ui.notify("Invalid username or password", color="negative")


@ui.page("/login")
def login_page():
    init_colors()

    with ui.dialog() as support_dialog, ui.card():
        ui.label("Novus Power Products").classes("text-h5")
        ui.label("novuspower.com")
        ui.label("(816) 836-7446")
        ui.label("support@novuspower.com")
        ui.button("Close", on_click=support_dialog.close).classes("bg-secondary")

    with ui.column(align_items="center").classes("absolute-center gap-16"):
        ui.image(str(ASSETS_DIR / "NOVUS_LOGO.svg")).classes("w-128 max-w-128")

        with ui.card():
            username = ui.input("Username")
            password = ui.input("Password", password=True, password_toggle_button=True)

            async def on_login():
                await try_login(username.value, password.value)

            username.on("keydown.enter", on_login)
            password.on("keydown.enter", on_login)

            with ui.row():
                ui.button("Log in", on_click=on_login).classes("bg-secondary")

                ui.button(
                    "Support",
                    on_click=support_dialog.open,
                ).classes("bg-secondary")
