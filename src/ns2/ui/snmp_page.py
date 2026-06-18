import asyncio

from nicegui import ui
from dataclasses import asdict

from ns2.utils import (
    ASSETS_DIR,
    log,
    validate_group,
    make_col_of,
    add_header_slot,
    make_action_col,
)
from dbus_next import Message
from ns2.lib.bridge import BridgeCall, GetBridge
from ns2.lib.systemd1 import isActive, SystemdStop, SystemdStart, SystemdRestart

from ns2.lib.snmp import are_you_sure_you_want_to

from ns2.ui.snmpDialogs import (
    AddV3UserDialog,
    AddV2UserDialog,
    AddV2TrapDialog,
    AddV3TrapDialog,
    editDeleteV2User,
    editDeleteV3User,
    editDeleteV2Trap,
    editDeleteV3Trap,
)


async def handleNotifications():
    await asyncio.sleep(0.25)
    v2UserTable.refresh()
    v2TrapsTable.refresh()
    v3UserTable.refresh()
    v3TrapsTable.refresh()
    snmp_state.refresh()
    snmp_status.refresh()


def notification_handler(msg: Message):
    if msg.interface == "com.novus.ns.snmp" and msg.member == "Changed":
        log.info(msg.body)
        asyncio.ensure_future(handleNotifications())
        return True


async def SetupSnmpNotifications():
    await BridgeCall(
        destination="org.freedesktop.DBus",
        path="/org/freedesktop/DBus",
        interface="org.freedesktop.DBus",
        member="AddMatch",
        signature="s",
        body=["type='signal',member='Changed',interface='com.novus.ns.snmp'"],
    )

    bridge = GetBridge()

    bridge.add_message_handler(notification_handler)


@ui.refreshable
async def snmp_state():
    snmpState = await isActive("snmpd.service")
    snmpStatus = "Enabled" if snmpState else "Disabled"

    async def snmp_switch_cb(e):
        action = "enable" if e.sender.value else "disable"
        with ui.dialog() as dialog, ui.card():
            ui.label(f"Are you sure you want to {action} snmpd?")
            with ui.row():
                ui.button("Cancel", on_click=lambda: dialog.submit("Cancel")).props(
                    "flat"
                )
                ui.button(f"{action}", on_click=lambda: dialog.submit(action)).props(
                    "flat"
                )
        result = await dialog
        active = (await isActive("snmpd.service")).get("state", False)
        if result == "enable" and not active:
            err = await SystemdStart("snmpd.service")
            if err:
                ui.notify(err, type="warning")
        if result == "disable" and active:
            err = await SystemdStop("snmpd.service")
            if err:
                ui.notify(err, type="warning")
        await snmp_state.refresh()

    ui.switch(f"Status: {snmpStatus}").on("click", lambda e: snmp_switch_cb(e)).props(
        "flat dense"
    ).bind_value(snmpState, "state")


@ui.refreshable
async def snmp_status():

    with ui.column() as status:
        ui.label("SNMP").classes("text-h5")

        async def snmp_reset_cb(e):
            result = await are_you_sure_you_want_to("reset the snmp config?")
            if result:

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

        with ui.card().classes("w-full").props("flat"):
            with ui.row().classes("items-center").props("dense"):

                await snmp_state()

                ui.button(
                    "Download MIB",
                    on_click=lambda: download_mib_cb(),
                ).props("flat")

                async def download_mib_cb():
                    with open(str(ASSETS_DIR / "NOVUS-SECURE-MIB_REV1.3.mib")) as f:
                        content = f.read()
                        ui.download.content(
                            content, filename="NOVUS-SECURE-MIB_REV1.3.mib"
                        )

                ui.button("Reset SNMPD Config", on_click=snmp_reset_cb).props("flat")

    return status


@ui.refreshable
async def v2UserTable():

    v2Users = await BridgeCall(
        "com.novus.ns", "/com/novus/ns", "com.novus.ns.snmp", "GetV2Users", "", []
    )

    v2Users = v2Users.body[0]

    dialog = await AddV2UserDialog()

    tab = (
        ui.table(
            title="v2 Users",
            rows=v2Users,
            columns=[
                make_col_of("Version"),
                make_col_of("Community"),
                make_col_of("Source"),
                make_col_of("Permissions"),
                make_action_col(),
            ],
            column_defaults={
                "align": "left",
                "headerClasses": "uppercase text-primary",
            },
        )
        .props("flat dense")
        .classes("w-full")
    )

    with tab.add_slot("top-right"):
        with ui.row():
            ui.input("Search").bind_value(tab, "filter").props("dense")
            ui.button(icon="add", on_click=dialog.open).props("dense flat")

    async def on_delete_cb(e):
        dialog = await editDeleteV2User(e.args)
        result = await dialog
        if result:
            ui.notify(result)

    with tab.add_slot("body-cell-action"):
        with tab.cell().props("align=right"):
            ui.button(icon="more_vert").props("flat").on(
                "click",
                js_handler="() => emit(props.row.Community)",
                handler=on_delete_cb,
            ).props("dense align=right")


@ui.refreshable
async def v2TrapsTable():

    dialog = await AddV2TrapDialog()

    rsp = await BridgeCall(
        "com.novus.ns", "/com/novus/ns", "com.novus.ns.snmp", "GetV2Traps", "", []
    )

    traps = rsp.body[0]

    log.info(f"v2 traps: {traps}")

    tab = (
        ui.table(
            title="v2 Traps",
            rows=traps,
            columns=[
                make_col_of("Version"),
                make_col_of("Community"),
                make_col_of("Protocol"),
                make_col_of("Host"),
                make_col_of("Port"),
                make_action_col(),
            ],
            column_defaults={
                "align": "left",
                "headerClasses": "uppercase text-primary",
            },
        )
        .props("flat dense")
        .classes("w-full")
    )

    with tab.add_slot("top-right"):
        with ui.row():
            ui.input("Search").bind_value(tab, "filter").props("dense")
            ui.button(icon="add", on_click=dialog.open).props("dense flat")

    async def on_delete_cb(e):
        dialog = await editDeleteV2Trap(e.args)
        result = await dialog
        if result:
            ui.notify(result)

    with tab.add_slot("body-cell-action"):
        with tab.cell().props("align=right"):
            ui.button(icon="more_vert").props("flat").on(
                "click",
                js_handler="() => emit(props.row.Community)",
                handler=on_delete_cb,
            ).props("dense")


@ui.refreshable
async def v3UserTable():

    v3Users = await BridgeCall(
        "com.novus.ns", "/com/novus/ns", "com.novus.ns.snmp", "GetV3Users", "", []
    )

    v3Users = v3Users.body[0]

    dialog = await AddV3UserDialog()

    tab = (
        ui.table(
            title="v3 Users",
            rows=v3Users,
            columns=[
                make_col_of("Username"),
                make_col_of("EngineId"),
                make_col_of("Permissions"),
                make_col_of("AuthType"),
                make_col_of("PrivType"),
                make_action_col(),
            ],
            column_defaults={
                "align": "left",
                "headerClasses": "uppercase text-primary",
            },
        )
        .props("flat dense")
        .classes("w-full")
    )

    with tab.add_slot("top-right"):
        with ui.row():
            ui.input("Search").bind_value(tab, "filter").props("dense")
            ui.button(icon="add", on_click=dialog.open).props("dense flat")

    async def on_delete_cb(e):
        dialog = await editDeleteV3User(e.args)
        result = await dialog
        if result:
            ui.notify(result)

    with tab.add_slot("body-cell-action"):
        with tab.cell().props("align=right"):
            ui.button(icon="more_vert").props("flat").on(
                "click",
                js_handler="() => emit(props.row.Username)",
                handler=on_delete_cb,
            ).props("dense")


@ui.refreshable
async def v3TrapsTable():

    dialog = await AddV3TrapDialog()

    rsp = await BridgeCall(
        "com.novus.ns", "/com/novus/ns", "com.novus.ns.snmp", "GetV3Traps", "", []
    )

    if rsp.error_name is not None:
        ui.notify(rsp.body[0])
        return

    traps = rsp.body[0]

    log.info(f"got v3 traps {traps}")

    tab = (
        ui.table(
            title="v3 Traps",
            rows=traps,
            columns=[
                make_col_of("Username"),
                make_col_of("EngineId"),
                make_col_of("AuthType"),
                make_col_of("PrivType"),
                make_col_of("Protocol"),
                make_col_of("Host"),
                make_col_of("Port"),
                make_action_col(),
            ],
            column_defaults={
                "align": "left",
                "headerClasses": "uppercase text-primary",
            },
        )
        .props("flat dense")
        .classes("w-full")
    )

    with tab.add_slot("top-right"):
        with ui.row():
            ui.input("Search").bind_value(tab, "filter").props("dense")
            ui.button(icon="add", on_click=dialog.open).props("dense flat")

    async def on_delete_cb(e):
        dialog = await editDeleteV3Trap(e.args)
        result = await dialog
        if result:
            ui.notify(result)

    with tab.add_slot("body-cell-action"):
        with tab.cell().props("align=right"):
            ui.button(icon="more_vert").props("flat").on(
                "click",
                js_handler="() => emit(props.row.Username)",
                handler=on_delete_cb,
            ).props("dense")


async def snmp_page():

    await SetupSnmpNotifications()

    await snmp_status()
    with ui.column().classes("w-full"):
        await v2UserTable()
        await v2TrapsTable()
        await v3UserTable()
        await v3TrapsTable()
