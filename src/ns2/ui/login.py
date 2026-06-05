from nicegui import ui, app
from ns2.ui.theme import init_colors
from ns2.utils import ASSETS_DIR
from ns2.lib.bridge import CallPamAuthenticate
from ns2.lib.bridge import SetupBridge, CleanupBridge
import uuid

from ns2.utils import log


async def logout_cb():
    ui.navigate.to("/login")
    app.storage.general.clear()
    log.info("logout cb general cleared")
    rsp = await CleanupBridge()
    if rsp:
        log.info("log out cleanup", rsp.body[0])


async def try_login(_username: str, _password: str) -> None:

    rsp = await CallPamAuthenticate(_username, _password)

    if rsp.error_name is not None:
        ui.notify(rsp.body[0])
        auth = False
    else:
        auth = rsp

    if auth:
        activeUser = await SetupBridge(_username)
        if activeUser != _username:
            ui.notify("active != _user")
            return
        print(activeUser)
        if not app.storage.user.get("uid"):
            app.storage.user.update({"uid": str(uuid.uuid4())})

        uid = app.storage.user.get("uid")
        log.info("try login general store updated")
        app.storage.general.update({"activeUser": activeUser, "uid": uid})
        ui.navigate.to("/")

    else:
        ui.notify("Invalid username or password", color="negative")


@ui.page("/login")
async def login_page():
    log.info("LOGIN PAGE LOADED")

    init_colors()
    with ui.dialog() as support_dialog, ui.card():
        ui.label("Novus Power Products").classes("text-h5")
        ui.label("novuspower.com")
        ui.label("(816) 836-7446")
        ui.label("support@novuspower.com")
        ui.button("Close", on_click=support_dialog.close).classes("bg-secondary")

    with ui.column(align_items="center").classes("absolute-center gap-16"):
        ui.image(str(ASSETS_DIR / "NOVUS_LOGO.svg")).classes("w-128 max-w-128")

        with ui.card().props("flat"):
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
