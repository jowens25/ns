from nicegui import ui, app, binding

from ns_admin.lib.accounts_lib import *
from ns_admin.api.main import get_dbus


# username
# password
# repeat password

# 12 chars, lower case, upper case, special char
#
# group: admin, user


@binding.bindable_dataclass
class User:
    Username: Optional[str] = ""
    Password: Optional[str] = ""
    PasswordRules: Optional[str] = ""
    Group: Optional[str] = "admin"


def editUserDialog(user):
    with ui.dialog() as dialog:
        with ui.card().classes("w-full max-h-[90vh] overflow-y-auto"):
            ui.label("Edit user").classes("text-h5")
            ui.button("close", on_click=dialog.close)

    return dialog


def deleteUserDialog(user):
    with ui.dialog() as dialog:
        with ui.card().classes("w-full max-h-[90vh] overflow-y-auto"):
            ui.label(f"Delete Account").classes("text-h5")
            ui.label(f"Are you sure you want to delete {user}")
            with ui.row():
                ui.button("Cancel", on_click=dialog.close())

                async def on_delete_cb(user):
                    print("CALL delete DBUS")
                    bus = await get_dbus()

                    dialog.submit(f"DELETED!!! {user} RESULTS")

                ui.button("Delete", on_click=on_delete_cb)

    return dialog


def addUserDialog():
    newUser = User()
    with ui.dialog() as dialog:
        with ui.card().classes("w-full max-h-[90vh] overflow-y-auto"):
            ui.label("Add user").classes("text-h5")
            ui.button("close", on_click=dialog.close)

            ui.input("username").bind_value(newUser, "Username")

            ui.input("password")

            ui.input("repeat password").bind_value_to(newUser, "Password")

            ui.label(newUser.PasswordRules)

            ui.select(["admin", "user"]).bind_value(newUser, "Group")

    return dialog
    # with ui.column().classes("w-full"):


#
#    ### ADDRESSES
#    with ui.row().classes("w-full justify-between"):
#        ui.label("Addresses")
#        with ui.row():
#
#            def on_method_change(e):
#                # SetIp4Method(settings, e.value)
#                return
#
#            ui.select(
#                options=["disabled", "auto", "manual"],
#                on_change=on_method_change,
#            ).props("dense").classes("w-24").bind_value(ip, "Method")
#
#            ip_address_button = ui.button(
#                icon="add", on_click=add_ip_address
#            ).props("flat color=accent dense")
#
#    with ui.column().classes("items-center justify-between gap-4 w-full"):
#        await ip_address_list()
#        print()
#    ###
#
#    ### DNS SERVER
#    ui.separator()
#    with ui.row().classes("w-full justify-between"):
#        ui.label("DNS Servers")
#        with ui.row():
#
#            dns_server_switch = (
#                ui.switch("Automatic")
#                .props("flat color=accent dense")
#                .classes("w-24")
#                .bind_value(
#                    ip,
#                    "IgnoreAutoDns",
#                    forward=lambda x: not x,
#                    backward=lambda x: not x,
#                )
#            )
#            dns_server_button = ui.button(
#                icon="add",
#                on_click=add_dns_server,
#            ).props("flat color=accent dense")
#    with ui.column().classes("items-center justify-between gap-4 w-full"):
#        await dns_server_list()
#    ###
#
#    ### DNS SEARCH
#    ui.separator()
#    with ui.row().classes("w-full justify-between"):
#        ui.label("DNS Searches")
#        with ui.row():
#            dns_search_button = (
#                ui.button(
#                    icon="add",
#                    on_click=add_dns_search,
#                )
#                .props("flat color=accent")
#                .props("dense")
#            )
#    with ui.column().classes("items-center justify-between gap-4 w-full"):
#        await dns_search_list()
#    ###
#
#    ### ROUTES
#    ui.separator()
#    with ui.row().classes("w-full justify-between"):
#        ui.label("Routes")
#        with ui.row():
#            route_switch = (
#                ui.switch("Automatic")
#                .props("flat color=accent")
#                .props("dense")
#                .classes("w-24")
#                .bind_value(
#                    ip,
#                    "IgnoreAutoRoutes",
#                    forward=lambda x: not x,
#                    backward=lambda x: not x,
#                )
#            )
#            route_button = (
#                ui.button(icon="add", on_click=add_route)
#                .props("flat color=accent")
#                .props("dense")
#            )
#    with ui.column().classes("items-center justify-between gap-4 w-full"):
#        await route_list()
#    ###
#
#    with ui.row().classes("items-center justify-between gap-4 w-full"):
#
#        async def on_save_cb():
#            try:
#
#                _settings = SetIp(ip, version, settings)
#
#                _settings = ApplyModes(version, _settings)
#
#                await connection.call_update2(_settings, 0x1, {})
#
#                await device.call_reapply(_settings, 0, 0)
#
#                dialog.close()
#
#            except DBusError as e:
#                ui.notify(e, type="negative")
#                # dialog.close()
#
#            except Exception as e:
#                print(e)
#                ui.notify("Please correct the errors", type="negative")
#
#        def on_cancel_cb():
#            dialog.close()
#
#        save_button = ui.button("save", on_click=on_save_cb).props(
#            "flat color=accent align=left"
#        )
#        cancel_button = ui.button("cancel", on_click=on_cancel_cb).props(
#            "flat color=accent align=left"
#        )
# return dialog
