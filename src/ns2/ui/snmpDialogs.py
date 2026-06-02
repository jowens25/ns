from nicegui import ui

from ns2.lib.snmp import V2Trap, V2User, V3User, V3Trap
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


async def createV2UserDialog():
    with ui.dialog() as createV2Dialog:
        v2 = V2User()

        with ui.card().classes("w-full"):
            with ui.column().classes("w-full"):
                version = (
                    ui.select(label="Version", options=["v2c", "v1"])
                    .classes("w-full")
                    .props("dense")
                    .bind_value(v2, "Version")
                )
                permissions = (
                    ui.select(
                        label="Permissions", options=["rwnoauthgroup", "ronoauthgroup"]
                    )
                    .classes("w-full")
                    .props("dense")
                    .bind_value(v2, "Permissions")
                )
                community = (
                    ui.input(
                        "Community",
                        validation={"Community required": lambda value: len(value) > 0},
                    )
                    .classes("w-full")
                    .props("dense")
                    .bind_value(v2, "Community")
                )
                source = (
                    ui.input("Source / IP Address", validation=sourceValidation)
                    .classes("w-full")
                    .props("dense")
                    .bind_value(v2, "Source")
                )
                with ui.row().classes("items-center justify-between gap-4 w-full"):

                    async def on_save_cb():
                        if all(
                            validate_group([version, permissions, community, source])
                        ):
                            await BridgeCall(
                                "com.novus.ns",
                                "/com/novus/ns",
                                "com.novus.ns.snmp",
                                "CreateV2User",
                                "a{ss}",
                                [asdict(v2)],
                            )
                            createV2Dialog.close()
                        else:
                            ui.notify("Please correct the errors", type="negative")

                    ui.button("save", on_click=on_save_cb).props("flat")
                    ui.button(icon="cancel", on_click=createV2Dialog.close).props(
                        "flat"
                    )

    return createV2Dialog


async def AddV2TrapDialog():
    newTrap = V2Trap()
    with ui.dialog() as dialog:
        with ui.card().classes("w-full max-h-[90vh] overflow-y-auto"):
            ui.label("Add v2 trap").classes("text-h5")

            version = (
                ui.select(["1", "2c"], label="Version", value="2c")
                .bind_value(newTrap, "Version")
                .classes("w-full")
                .props("dense")
            )

            community = (
                ui.input("Community")
                .bind_value(newTrap, "Community")
                .classes("w-full")
                .props("dense")
            )

            protocol = (
                ui.select(["udp", "tcp", "upd6", "tcp6"], label="Protocol")
                .bind_value(newTrap, "Protocol")
                .classes("w-full")
                .props("dense")
            )
            host = (
                ui.input("Host")
                .bind_value(newTrap, "Host")
                .classes("w-full")
                .props("dense")
            )
            port = (
                ui.input("Port", validation=portValidation)
                .bind_value(newTrap, "Port")
                .classes("w-full")
                .props("dense")
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

            with ui.row():
                ui.button("Add", on_click=on_save_cb)
                ui.button("Cancel", on_click=dialog.close)

    return dialog


async def AddV3TrapDialog():
    newTrap = V3Trap()
    with ui.dialog() as dialog:
        with ui.card().classes("w-full max-h-[90vh] overflow-y-auto"):
            ui.label("Add V3 trap").classes("text-h5")

            ui.input("Engine ID").bind_value(newTrap, "EngineId").classes(
                "w-full"
            ).props("dense")
            ui.input("Username").bind_value(newTrap, "Username").classes(
                "w-full"
            ).props("dense")

            ui.select(
                ["MD5", "SHA"], label="Authentication Type", value="MD5"
            ).bind_value(newTrap, "AuthType").classes("w-full").props("dense")

            ui.select(["DES", "AES"], label="Privacy Type", value="DES").bind_value(
                newTrap, "PrivType"
            ).classes("w-full").props("dense")

            protocol = (
                ui.select(["udp", "tcp", "upd6", "tcp6"], label="Protocol")
                .bind_value(newTrap, "Protocol")
                .classes("w-full")
                .props("dense")
            )
            host = ui.input("Host").bind_value(newTrap, "Host").classes("w-full")
            port = (
                ui.input("Port", validation=portValidation)
                .bind_value(newTrap, "Port")
                .classes("w-full")
                .props("dense")
            )

            async def on_save_cb():
                if all(validate_group([port])):
                    log.info(asdict(newTrap))

                    rsp = await BridgeCall(
                        "com.novus.ns",
                        "/com/novus/ns",
                        "com.novus.ns.snmp",
                        "CreateV3Trap",
                        "a{ss}",
                        [asdict(newTrap)],
                    )
                    rsp = rsp.body[0]

                    log.info(rsp)
                    dialog.close()
                else:
                    ui.notify("Please correct the errors", type="negative")

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


async def edit_delete_v2_user_card(community):

    with ui.dialog() as dialog:
        user = await BridgeCall(
            "com.novus.ns",
            "/com/novus/ns",
            "com.novus.ns.snmp",
            "GetV2UserByCommunity",
            "s",
            [community],
        )
        user = user.body[0]
        v2User = V2User(**user)
        with ui.card().classes("w-full").props("flat"):
            with ui.column().classes("w-full"):
                version = (
                    ui.select(label="Version", options=["v2c", "v1"])
                    .classes("w-full")
                    .bind_value(v2User, "Version")
                )
                permissions = (
                    ui.select(
                        label="Permissions", options=["rwnoauthgroup", "ronoauthgroup"]
                    )
                    .classes("w-full")
                    .bind_value(v2User, "Permissions")
                )
                community = (
                    ui.input(
                        "Community",
                        validation={"Community required": lambda value: len(value) > 0},
                    )
                    .classes("w-full")
                    .bind_value(v2User, "Community")
                )
                source = (
                    ui.input("Source / IP Address", validation=sourceValidation)
                    .classes("w-full")
                    .bind_value(v2User, "Source")
                )
                with ui.row().classes("items-center justify-between gap-4 w-full"):

                    async def on_save_cb():

                        await BridgeCall(
                            "com.novus.ns",
                            "/com/novus/ns",
                            "com.novus.ns.snmp",
                            "ModifyV2User",
                            "a{ss}",
                            [asdict(v2User)],
                        )

                    async def on_delete_cb():
                        with ui.dialog() as dialog, ui.card().props("flat"):
                            ui.label(
                                f"Are you sure you want to delete {v2User.Community}?"
                            )
                            with ui.row():
                                ui.button(
                                    "Yes", on_click=lambda: dialog.submit(True)
                                ).props("flat")
                                ui.button(
                                    "No", on_click=lambda: dialog.submit(False)
                                ).props("flat")
                        result = await dialog
                        if result:
                            await BridgeCall(
                                "com.novus.ns",
                                "/com/novus/ns",
                                "com.novus.ns.snmp",
                                "RemoveV2User",
                                "a{ss}",
                                [asdict(v2User)],
                            )

                            ui.notify(f"User {v2User.Community} deleted...")
                        else:
                            dialog.close()

                    ui.button("save", on_click=on_save_cb).props("flat align=left")
                    ui.button(icon="delete", on_click=on_delete_cb).props("flat")
                    ui.button(icon="cancel", on_click=dialog.close).props("flat")

    return dialog


async def edit_delete_v3_user_card(username):
    with ui.dialog() as dialog:
        userData = await BridgeCall(
            "com.novus.ns",
            "/com/novus/ns",
            "com.novus.ns.snmp",
            "GetV3UserByUsername",
            "s",
            [username],
        )
        userData = userData.body[0]
        initUser = V3User(**userData)
        finalUser = V3User(**userData)

        with ui.card().classes("w-full"):
            with ui.column().classes("w-full"):

                version = (
                    ui.input(label="Version")
                    .classes("w-full")
                    .bind_value(finalUser, "Version")
                )
                version.disable()
                username = (
                    ui.input(label="Username", validation=usernameValidation)
                    .classes("w-full")
                    .bind_value(finalUser, "Username")
                )
                permissions = (
                    ui.select(
                        label="Permissions", options=["roprivgroup", "rwprivgroup"]
                    )
                    .classes("w-full")
                    .bind_value(finalUser, "Permissions")
                )
                auth_type = (
                    ui.select(label="Auth Alg", options=["SHA", "MD5"])
                    .classes("w-full")
                    .bind_value(finalUser, "AuthType")
                )
                auth_pass = (
                    ui.input(label="Auth Passphrase", validation=passphraseValidation)
                    .classes("w-full")
                    .bind_value(finalUser, "AuthPassphrase")
                )
                priv_type = (
                    ui.select(label="Priv Alg", options=["AES", "DES"])
                    .classes("w-full")
                    .bind_value(finalUser, "PrivType")
                )
                priv_pass = (
                    ui.input(label="Auth Passphrase", validation=passphraseValidation)
                    .classes("w-full")
                    .bind_value(finalUser, "PrivPassphrase")
                )

                with ui.row().classes("items-center justify-between gap-4 w-full"):

                    async def on_save_cb():
                        disable_group(group)
                        save_button.enabled = False
                        edit_button.enabled = True
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

                            await BridgeCall(
                                "com.novus.ns",
                                "/com/novus/ns",
                                "com.novus.ns.snmp",
                                "ModifyV3User",
                                "a{ss}",
                                [asdict(initUser), [asdict(finalUser)]],
                            )

                        else:
                            ui.notify("Please correct the errors", type="negative")

                    async def on_delete_cb():
                        with ui.dialog() as dialog, ui.card():
                            ui.label(
                                f"Are you sure you want to delete {initUser.Username}?"
                            )
                            with ui.row():
                                ui.button(
                                    "Yes", on_click=lambda: dialog.submit(True)
                                ).props("flat color=accent align=left")
                                ui.button(
                                    "No", on_click=lambda: dialog.submit(False)
                                ).props("flat color=accent align=left")
                        result = await dialog
                        if result:
                            await BridgeCall(
                                "com.novus.ns",
                                "/com/novus/ns",
                                "com.novus.ns.snmp",
                                "RemoveV3User",
                                "a{ss}",
                                [asdict(initUser)],
                            )
                            # await DeleteV3User(AppBus, asdict(initUser))

                            ui.notify(f"User {initUser.Username} deleted...")
                        else:
                            dialog.close()

                    ui.button("save", on_click=on_save_cb).props("flat")
                    ui.button(icon="delete", on_click=on_delete_cb).props("flat")
                    ui.button(icon="cancel", on_click=dialog.close).props("flat")

    return dialog
