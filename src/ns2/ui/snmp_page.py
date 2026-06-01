from nicegui import ui
from dataclasses import asdict

from ns2.utils import log, validate_group
from dbus_next import Message
from ns2.lib.bridge import BridgeCall, GetBridge
from ns2.lib.systemd1 import isActive, SystemdStop, SystemdStart

from ns2.lib.snmp import V3User, V2User

from ns2.ui.snmpDialogs import create_v3_user_dialog


def notification_handler(msg: Message):
    if msg.interface == "com.novus.ns.accounts" and msg.member == "Changed":
        log.info(msg.body)
        accounts_table.refresh()
        return True


async def SetupNotifications():
    await BridgeCall(
        destination="org.freedesktop.DBus",
        path="/org/freedesktop/DBus",
        interface="org.freedesktop.DBus",
        member="AddMatch",
        signature="s",
        body=["type='signal',member='Changed',interface='com.novus.ns.accounts'"],
    )

    bridge = GetBridge()

    bridge.add_message_handler(notification_handler)


@ui.refreshable
async def v3table():

    v3Users = await BridgeCall(
        "com.novus.ns", "/com/novus/ns", "com.novus.ns.snmp", "GetV3Users", "", []
    )

    v3Users = v3Users.body[0]

    createV3Dialog = await create_v3_user_dialog()

    table = ui.table(
        title="v3 Users",
        rows=v3Users,
        column_defaults={
            "align": "left",
            "headerClasses": "uppercase text-primary",
        },
    ).classes("w-full")

    table.add_slot(
        f"body-cell-Username",
        f""" <q-td :props="props">
                   <a :href="'/snmp/v3/'+ props.row.Username" class="text-accent cursor-pointer hover:underline"> {{{{ props.value }}}} </a>
                   </q-td> """,
    )

    table.props(
        f'visible-columns={"Username,Version,EngineId,GroupName,AuthType,PrivType"}'
    )  # Only show these

    with table.add_slot("top-right"):
        ui.button(icon="add", on_click=createV3Dialog.open).props(
            "flat color=accent align=left"
        ).classes("w-full").props("dense")


@ui.refreshable
async def v2table():

    v2Users = await BridgeCall(
        "com.novus.ns", "/com/novus/ns", "com.novus.ns.snmp", "GetV2Users", "", []
    )

    v2Users = v2Users.body[0]

    log.info(v2Users)

    with ui.dialog() as createV2Dialog:
        v2 = V2User()
        v2.Version = "v2c"
        v2.Permissions = "rwnoauthgroup"
        v2.Source = "default"
        with ui.card().classes("w-full"):
            with ui.column().classes("w-full"):
                version = (
                    ui.select(label="Version", options=["v2c", "v1"])
                    .classes("w-full")
                    .bind_value(v2, "Version")
                )
                permissions = (
                    ui.select(
                        label="Permissions", options=["rwnoauthgroup", "ronoauthgroup"]
                    )
                    .classes("w-full")
                    .bind_value(v2, "Permissions")
                )
                community = (
                    ui.input(
                        "Community",
                        validation={"Community required": lambda value: len(value) > 0},
                    )
                    .classes("w-full")
                    .bind_value(v2, "Community")
                )
                source = (
                    ui.input("Source / IP Address", validation=sourceValidation)
                    .classes("w-full")
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
                            await v2table.refresh()
                            createV2Dialog.close()
                        else:
                            ui.notify("Please correct the errors", type="negative")

                    def on_cancel_cb():
                        createV2Dialog.close()

                    ui.button("save", on_click=on_save_cb).props(
                        "flat color=accent align=left"
                    )
                    ui.button(icon="cancel", on_click=on_cancel_cb).props(
                        "flat color=accent align=left"
                    )

    table = ui.table(
        title="v2 Users",
        rows=v2Users,
        column_defaults={
            "align": "left",
            "headerClasses": "uppercase text-primary",
        },
    ).classes("w-full")

    table.add_slot(
        "body-cell-Community",
        f"""
            <q-td :props="props">
                <a :href="'/snmp/v2/'+ props.row.Community" class="text-accent cursor-pointer hover:underline"> {{{{ props.value }}}} </a>
            </q-td>
        """,
    )

    table.props(
        f'visible-columns={"Community,Version,Source,GroupName"}'
    )  # Only show these

    with table.add_slot("top-right"):
        ui.button(icon="add", on_click=createV2Dialog.open).props(
            "flat color=accent align=left"
        ).classes("w-full").props("dense")


async def snmp_status():

    with ui.column() as status:
        ui.label("SNMP").classes("text-h5")

        async def snmp_switch_cb(e):
            action = "enable" if e.sender.value else "disable"
            with ui.dialog() as dialog, ui.card():
                ui.label(f"Are you sure you want to {action} snmp?")
                with ui.row():
                    ui.button("Cancel", on_click=lambda: dialog.submit("Cancel")).props(
                        "flat color=accent align=left"
                    )
                    ui.button(
                        f"{action}", on_click=lambda: dialog.submit(action)
                    ).props("flat color=accent align=left")

            result = await dialog
            active = await isActive("snmpd.service")

            if result == "enable" and not active:
                await SystemdStart("snmpd.service")

            if result == "disable" and active:
                await SystemdStop("snmpd.service")

            e.sender.value = await isActive("snmpd.service")

        async def snmp_reset_cb(e):
            with ui.dialog() as dialog, ui.card():
                ui.label("Are you sure you want to reset snmp?")
                with ui.row():
                    ui.button("Cancel", on_click=lambda: dialog.submit("Cancel")).props(
                        "flat color=accent align=left"
                    )
                    ui.button("Reset", on_click=lambda: dialog.submit("reset")).props(
                        "flat color=accent align=left"
                    )
            if await dialog == "reset":

                rsp = await BridgeCall(
                    "com.novus.ns",
                    "/com/novus/ns",
                    "com.novus.ns.snmp",
                    "Reset",
                    "",
                    [],
                )
                if rsp:
                    ui.notify(rsp.body[0], type="warning")
                v2table.refresh()
                v3table.refresh()

        with ui.card().classes("w-full"):
            snmp_service_switch = (
                ui.switch("SNMPD Status")
                .on("click", lambda e: snmp_switch_cb(e))
                .props("flat color=accent align=left dense")
            )
            snmp_service_switch.value = await isActive("snmpd.service")
            ui.button("Reset SNMPD Config", on_click=snmp_reset_cb).props(
                "flat color=accent align=left dense"
            )

    return status


async def v2Traps():

    addTrapDialog = await AddV2TrapDialog()

    traps = await BridgeCall(
        "com.novus.ns", "/com/novus/ns", "com.novus.ns.snmp", "ReadV2Traps", "", []
    )

    traps = traps.body[0]

    v2TrapsTable = ui.table(
        title="v2 Traps",
        rows=traps,
        column_defaults={
            "align": "left",
            "headerClasses": "uppercase text-primary",
        },
    ).classes("w-full")

    with v2TrapsTable.add_slot("top-right"):

        with ui.row():
            ui.input("Search").bind_value(v2TrapsTable, "filter").props("dense")

            ui.button(icon="add", on_click=addTrapDialog.open).props("dense")


async def snmp_page():

    await snmp_status()
    await v2table()  # Only show these

    await v2Traps()
    await v3table()


async def snmp_user_page(version: str, user: str):
    with ui.row():
        ui.link("SNMP", "/snmp")
        ui.label(">")
        ui.label(user)

        if version == "v2":
            await edit_delete_v2_user_card(user)
        if version == "v3":
            await edit_delete_v3_user_card(user)


def enable_group(fields):
    for f in fields:
        f.enabled = True


def disable_group(fields):
    for f in fields:
        f.enabled = False


async def edit_delete_v2_user_card(community):

    # user = await snmp.call_get_v2_user_by_community(community)
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
    with ui.card().classes("w-full"):
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
                    disable_group(group)
                    save_button.enabled = False
                    edit_button.enabled = True
                    await BridgeCall(
                        "com.novus.ns",
                        "/com/novus/ns",
                        "com.novus.ns.snmp",
                        "ModifyV2User",
                        "a{ss}",
                        [asdict(v2User)],
                    )
                    await v2table.refresh()
                    ui.navigate.back()

                def on_edit_cb():
                    enable_group(group)
                    edit_button.enabled = False
                    save_button.enabled = True

                async def on_delete_cb():
                    with ui.dialog() as dialog, ui.card():
                        ui.label(f"Are you sure you want to delete {v2User.Community}?")
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
                            "RemoveV2User",
                            "a{ss}",
                            [asdict(v2User)],
                        )
                        v2table.refresh()
                        ui.navigate.back()
                        ui.notify(f"User {v2User.Community} deleted...")
                    else:
                        dialog.close()

                edit_button = ui.button("edit", on_click=on_edit_cb).props(
                    "flat color=accent align=left"
                )
                save_button = ui.button("save", on_click=on_save_cb).props(
                    "flat color=accent align=left"
                )
                ui.button(icon="delete", on_click=on_delete_cb).props(
                    "flat color=accent align=left"
                )

                group = [community, source, version, permissions]

                disable_group(group)
                edit_button.enabled = True
                save_button.enabled = False


async def edit_delete_v3_user_card(username):

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
                ui.select(label="Permissions", options=["roprivgroup", "rwprivgroup"])
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
                        ui.navigate.back()
                    else:
                        ui.notify("Please correct the errors", type="negative")

                def on_edit_cb():
                    enable_group(group)
                    edit_button.enabled = False
                    save_button.enabled = True

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
                        ui.navigate.back()
                        ui.notify(f"User {initUser.Username} deleted...")
                    else:
                        dialog.close()

                edit_button = ui.button("edit", on_click=on_edit_cb).props(
                    "flat color=accent align=left"
                )
                save_button = ui.button("save", on_click=on_save_cb).props(
                    "flat color=accent align=left"
                )
                ui.button(icon="delete", on_click=on_delete_cb).props(
                    "flat color=accent align=left"
                )

                group = [
                    permissions,
                    username,
                    auth_type,
                    auth_pass,
                    priv_type,
                    priv_pass,
                ]

                disable_group(group)
                edit_button.enabled = True
                save_button.enabled = False
