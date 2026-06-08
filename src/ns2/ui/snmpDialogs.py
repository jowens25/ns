from nicegui import ui

from ns2.lib.snmp import V2Trap, V2User, V3User, V3Trap, are_you_sure_you_want_to
from ns2.utils import validate_group, log
from dataclasses import asdict
from ns2.lib.bridge import BridgeCall

from ns2.ui.snmpCards import (
    v2UserCardBody,
    v3TrapCardBody,
    v2TrapCardBody,
    v3UserCardBody,
)


async def AddV2UserDialog():
    v2 = V2User()
    with ui.dialog() as dialog, ui.card().classes("w-full"):
        with ui.column().classes("w-full"):
            elements = await v2UserCardBody(v2)
            with ui.row().classes("items-center justify-between gap-4 w-full"):

                async def on_save_cb():
                    if all(validate_group(elements)):
                        rsp = await BridgeCall(
                            "com.novus.ns",
                            "/com/novus/ns",
                            "com.novus.ns.snmp",
                            "CreateV2User",
                            "a{ss}",
                            [asdict(v2)],
                        )
                        ui.notify(rsp.body[0])
                        dialog.close()
                    else:
                        ui.notify("Please correct the errors", type="warning")

                with ui.row():
                    ui.button("Add", on_click=on_save_cb)
                    ui.button("Cancel", on_click=dialog.close)

    return dialog


async def AddV2TrapDialog():
    newTrap = V2Trap()
    with ui.dialog() as dialog, ui.card().classes("w-full"):

        ui.label("Add v2 trap").classes("text-h5")

        elements = await v2TrapCardBody(newTrap)

        async def on_save_cb():
            if all(validate_group(elements)):
                log.info(asdict(newTrap))

                rsp = await BridgeCall(
                    "com.novus.ns",
                    "/com/novus/ns",
                    "com.novus.ns.snmp",
                    "CreateV2Trap",
                    "a{ss}",
                    [asdict(newTrap)],
                )
                if rsp.error_name:
                    ui.notify(rsp.body[0])
                else:
                    dialog.close()
            else:
                ui.notify("Please correct the errors", type="warning")

        with ui.row():
            ui.button("Add", on_click=on_save_cb)
            ui.button("Cancel", on_click=dialog.close)

    return dialog


async def AddV3TrapDialog():
    newTrap = V3Trap()
    with ui.dialog() as dialog, ui.card().classes("w-full"):

        elements = await v3TrapCardBody(newTrap)

        async def on_save_cb():
            if all(validate_group(elements)):
                log.info(asdict(newTrap))

                rsp = await BridgeCall(
                    "com.novus.ns",
                    "/com/novus/ns",
                    "com.novus.ns.snmp",
                    "CreateV3Trap",
                    "a{ss}",
                    [asdict(newTrap)],
                )
                if rsp.error_name:
                    ui.notify(rsp.body[0])
                else:
                    dialog.close()
            else:
                ui.notify("Please correct the errors", type="warning")

        with ui.row():
            ui.button("Add", on_click=on_save_cb)
            ui.button("Cancel", on_click=dialog.close)

    return dialog


async def AddV3UserDialog():
    v3 = V3User()

    with ui.dialog() as dialog, ui.card().classes("w-full"):
        with ui.column().classes("w-full"):

            elements = await v3UserCardBody(v3)

            with ui.row().classes("items-center justify-between gap-4 w-full"):

                async def on_save_cb():
                    if all(validate_group(elements)):
                        log.info(asdict(v3))

                        rsp = await BridgeCall(
                            "com.novus.ns",
                            "/com/novus/ns",
                            "com.novus.ns.snmp",
                            "CreateV3User",
                            "a{ss}",
                            [asdict(v3)],
                        )
                        ui.notify(rsp.body[0])
                        dialog.close()
                    else:
                        ui.notify("Please correct the errors", type="warning")

                with ui.row():
                    ui.button("Add", on_click=on_save_cb)
                    ui.button("Cancel", on_click=dialog.close)

    return dialog


async def editDeleteV2User(community):
    log.info("editDeleteV2User")
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
    with ui.dialog() as dialog, ui.card().classes("w-full").props("flat"):
        with ui.column().classes("w-full"):
            elements = await v2UserCardBody(v2User)
            with ui.row().classes("items-center justify-between gap-4 w-full"):

                async def on_save_cb():
                    if all(validate_group(elements)):
                        rsp = await BridgeCall(
                            "com.novus.ns",
                            "/com/novus/ns",
                            "com.novus.ns.snmp",
                            "ModifyV2User",
                            "a{ss}",
                            [asdict(v2User)],
                        )

                        ui.notify(rsp.body[0])
                        dialog.close()
                    else:
                        ui.notify("Please correct the errors", type="warning")

                async def on_delete_cb():
                    result = await are_you_sure_you_want_to(
                        f"delete {v2User.Community}"
                    )
                    if result:
                        rsp = await BridgeCall(
                            "com.novus.ns",
                            "/com/novus/ns",
                            "com.novus.ns.snmp",
                            "RemoveV2User",
                            "a{ss}",
                            [asdict(v2User)],
                        )
                        ui.notify(rsp.body[0])
                        dialog.close()
                    else:
                        dialog.close()

                with ui.row():
                    ui.button("save", on_click=on_save_cb).props("flat")
                    ui.button("cancel", on_click=dialog.close).props("flat")
                ui.button(icon="delete", on_click=on_delete_cb).props("flat")

    return dialog


async def editDeleteV2Trap(community: str):
    rsp = await BridgeCall(
        "com.novus.ns",
        "/com/novus/ns",
        "com.novus.ns.snmp",
        "GetV2TrapByCommunity",
        "s",
        [community],
    )
    initTrap = V2Trap(**rsp.body[0])
    finalTrap = V2Trap(**rsp.body[0])

    log.info(f"a v2 trap: {finalTrap}")
    with ui.dialog() as dialog, ui.card().classes("w-full").props("flat"):
        with ui.column().classes("w-full"):

            elements = await v2TrapCardBody(finalTrap)

            with ui.row().classes("items-center justify-between gap-4 w-full"):

                async def on_save_cb():
                    if all(validate_group(elements)):
                        rsp = await BridgeCall(
                            "com.novus.ns",
                            "/com/novus/ns",
                            "com.novus.ns.snmp",
                            "ModifyV2Trap",
                            "a{ss}a{ss}",
                            [asdict(initTrap), asdict(finalTrap)],
                        )

                        ui.notify(rsp.body[0])
                        dialog.close()
                    else:
                        ui.notify("Please correct the errors", type="warning")

                async def on_delete_cb():
                    result = await are_you_sure_you_want_to(
                        f"delete {initTrap.Community}"
                    )
                    if result:
                        rsp = await BridgeCall(
                            "com.novus.ns",
                            "/com/novus/ns",
                            "com.novus.ns.snmp",
                            "RemoveV2Trap",
                            "a{ss}",
                            [asdict(initTrap)],
                        )

                        ui.notify(rsp.body[0])
                    else:
                        dialog.close()

                with ui.row():
                    ui.button("save", on_click=on_save_cb).props("flat")
                    ui.button("cancel", on_click=dialog.close).props("flat")
                ui.button(icon="delete", on_click=on_delete_cb).props("flat")

    return dialog


async def editDeleteV3User(username):

    rsp = await BridgeCall(
        "com.novus.ns",
        "/com/novus/ns",
        "com.novus.ns.snmp",
        "GetV3UserByUsername",
        "s",
        [username],
    )
    userData = rsp.body[0]
    initUser = V3User(**userData)
    finalUser = V3User(**userData)
    with ui.dialog() as dialog, ui.card().classes("w-full").props("flat"):

        with ui.column().classes("w-full"):

            elements = await v3UserCardBody(finalUser)

            with ui.row().classes("items-center justify-between gap-4 w-full"):

                async def on_save_cb():
                    if all(validate_group(elements)):
                        rsp = await BridgeCall(
                            "com.novus.ns",
                            "/com/novus/ns",
                            "com.novus.ns.snmp",
                            "ModifyV3User",
                            "a{ss}a{ss}",
                            [asdict(initUser), asdict(finalUser)],
                        )
                        ui.notify(rsp.body[0])
                        dialog.close()
                    else:
                        ui.notify("Please correct the errors", type="warning")

                async def on_delete_cb():
                    result = await are_you_sure_you_want_to(
                        f"delete {initUser.Username}"
                    )
                    if result:
                        rsp = await BridgeCall(
                            "com.novus.ns",
                            "/com/novus/ns",
                            "com.novus.ns.snmp",
                            "RemoveV3User",
                            "a{ss}",
                            [asdict(initUser)],
                        )

                        ui.notify(rsp.body[0])

                    else:
                        dialog.close()

                with ui.row():
                    ui.button("save", on_click=on_save_cb).props("flat")
                    ui.button("cancel", on_click=dialog.close).props("flat")
                ui.button(icon="delete", on_click=on_delete_cb).props("flat")

    return dialog


async def editDeleteV3Trap(username: str):
    rsp = await BridgeCall(
        "com.novus.ns",
        "/com/novus/ns",
        "com.novus.ns.snmp",
        "GetV3TrapByUsername",
        "s",
        [username],
    )
    initTrap = V3Trap(**rsp.body[0])
    finalTrap = V3Trap(**rsp.body[0])

    log.info(f"a v3 trap: {finalTrap}")
    with ui.dialog() as dialog, ui.card().classes("w-full").props("flat"):
        with ui.column().classes("w-full"):

            elements = await v3TrapCardBody(finalTrap)

            with ui.row().classes("items-center justify-between gap-4 w-full"):

                async def on_save_cb():
                    if all(validate_group(elements)):
                        rsp = await BridgeCall(
                            "com.novus.ns",
                            "/com/novus/ns",
                            "com.novus.ns.snmp",
                            "ModifyV3Trap",
                            "a{ss}a{ss}",
                            [asdict(initTrap), asdict(finalTrap)],
                        )

                        ui.notify(rsp.body[0])
                        dialog.close()
                    else:
                        ui.notify("Please correct the errors", type="warning")

                async def on_delete_cb():
                    result = await are_you_sure_you_want_to(
                        f"delete {initTrap.Username}"
                    )
                    if result:
                        rsp = await BridgeCall(
                            "com.novus.ns",
                            "/com/novus/ns",
                            "com.novus.ns.snmp",
                            "RemoveV3Trap",
                            "a{ss}",
                            [asdict(initTrap)],
                        )

                        ui.notify(rsp.body[0])

                    else:
                        dialog.close()

                with ui.row():
                    ui.button("save", on_click=on_save_cb).props("flat")
                    ui.button("cancel", on_click=dialog.close).props("flat")
                ui.button(icon="delete", on_click=on_delete_cb).props("flat")

    return dialog
