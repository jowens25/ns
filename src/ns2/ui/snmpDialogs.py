from nicegui import ui

from ns2.lib.snmp import V2Trap, V2User, V3User
from ns2.utils import validate_group, log
from dataclasses import asdict
from ns2.lib.bridge import BridgeCall

portValidation = {
    "Port must be a number": lambda value: value.isdigit(),
}


usernameValidation = {
    "Username must be at least 5 characters": lambda value: len(value) >= 5,
    "Username must be 24 or less characaters": lambda value: 24 >= len(value),
}


sourceValidation = {
    "Please enter a valid ip address, network or default": lambda value: len(value) > 0
}
passphraseValidation = {
    "Passphrase must be at least 8 characters": lambda value: len(value) >= 8,
    "Passphrase must be 24 or less characaters": lambda value: 24 >= len(value),
}


async def AddV2TrapDialog():
    newTrap = V2Trap()
    with ui.dialog() as dialog:
        with ui.card().classes("w-full max-h-[90vh] overflow-y-auto"):
            ui.label("Add trap").classes("text-h5")

            version = ui.select(["1, 2c"], label="Version", value="2c").bind_value(
                newTrap, "Version"
            )

            community = ui.input("Community").bind_value(newTrap, "Community")

            protocol = ui.select(
                ["udp", "tcp", "upd6", "tcp6"], label="Protocol"
            ).bind_value(newTrap, "Protocol")
            host = ui.input("Host").bind_value(newTrap, "Host")
            port = ui.input("Port", validation=portValidation).bind_value(
                newTrap, "Port"
            )

            async def on_save_cb():
                if all(validate_group([port])):
                    log.info(asdict(newTrap))

                    rsp = await BridgeCall(
                        "com.novus.ns",
                        "/com/novus/ns",
                        "com.novus.ns.snmp",
                        "CreateV3User",
                        "a{ss}",
                        [asdict(newTrap)],
                    )
                    rsp = rsp.body[0]

                    log.info(rsp)
                    dialog.close()
                else:
                    ui.notify("Please correct the errors", type="negative")

            def on_cancel_cb():
                dialog.close()

            with ui.row():
                ui.button("Add", on_click=on_save_cb)
                ui.button("Cancel", on_click=dialog.close)

    return dialog


async def create_v3_user_dialog():
    with ui.dialog() as createV3Dialog:
        v3 = V3User()
        with ui.card().classes("w-full"):
            with ui.column().classes("w-full"):
                version = (
                    ui.input(label="Version")
                    .classes("w-full")
                    .bind_value(v3, "Version")
                )
                version.disable()
                username = (
                    ui.input(label="Username", validation=usernameValidation)
                    .classes("w-full")
                    .bind_value(v3, "Username")
                ).props("debounce=1000")
                permissions = (
                    ui.select(
                        label="Permissions", options=["roprivgroup", "rwprivgroup"]
                    )
                    .classes("w-full")
                    .bind_value(v3, "Permissions")
                )
                auth_type = (
                    ui.select(label="Auth Alg", options=["SHA", "MD5"])
                    .classes("w-full")
                    .bind_value(v3, "AuthType")
                )
                auth_pass = (
                    ui.input(label="Auth Passphrase", validation=passphraseValidation)
                    .classes("w-full")
                    .bind_value(v3, "AuthPassphrase")
                ).props("debounce=1000")
                priv_type = (
                    ui.select(label="Priv Alg", options=["AES", "DES"])
                    .classes("w-full")
                    .bind_value(v3, "PrivType")
                )
                priv_pass = (
                    ui.input(label="Auth Passphrase", validation=passphraseValidation)
                    .classes("w-full")
                    .bind_value(v3, "PrivPassphrase")
                ).props("debounce=1000")
                with ui.row().classes("items-center justify-between gap-4 w-full"):

                    async def on_save_cb():
                        if all(
                            validate_group(
                                [
                                    version,
                                    username,
                                    permissions,
                                    auth_type,
                                    auth_pass,
                                    priv_type,
                                    priv_pass,
                                ]
                            )
                        ):
                            log.info(asdict(v3))

                            rsp = await BridgeCall(
                                "com.novus.ns",
                                "/com/novus/ns",
                                "com.novus.ns.snmp",
                                "CreateV3User",
                                "a{ss}",
                                [asdict(v3)],
                            )
                            rsp = rsp.body[0]

                            log.info(rsp)
                            createV3Dialog.close()
                        else:
                            ui.notify("Please correct the errors", type="negative")

                    def on_cancel_cb():
                        createV3Dialog.close()

                    ui.button("save", on_click=on_save_cb).props(
                        "flat color=accent align=left"
                    )
                    ui.button(icon="cancel", on_click=on_cancel_cb).props(
                        "flat color=accent align=left"
                    )

    return createV3Dialog
