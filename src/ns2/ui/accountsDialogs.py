from typing import Optional

from nicegui import ui, binding

from ns2.lib.bridge import BridgeCall

from dbus_next.signature import Variant
from dbus_next import Message

from ns2.utils import log

from ns2.lib.accounts import ValidatePassword


@binding.bindable_dataclass
class User:
    Username: Optional[str] = ""
    Password: Optional[str] = ""
    PasswordRules: Optional[str] = ""
    Group: Optional[str] = "admin"


def editUserDialog(username):
    editUser = User(Username=username)
    with ui.dialog() as dialog:
        with ui.card().classes("w-full max-h-[90vh] overflow-y-auto"):
            ui.label("Edit user").classes("text-h5")
            user = ui.input("username", validation=usernameValidation).bind_value(
                editUser, "Username"
            )

            def mustMatch(v):
                if not v == p1.value:
                    return "passwords must match"
                else:
                    return None

            p1 = ui.input("password", validation=validatePass)

            p2 = ui.input("repeat password", validation=mustMatch).bind_value_to(
                editUser, "Password"
            )

            ui.select(["admin", "user"]).bind_value(editUser, "Group")

            async def on_save_cb():
                if all(validate_group([p1, p2, user])):

                    rsp = await EditUser(editUser)

                    if rsp.error_name is not None:
                        ui.notify(rsp.body[0])
                    else:
                        ui.notify(rsp, type="positive")
                        dialog.close()

                else:
                    ui.notify("Please correct the errors", type="negative")

            with ui.row():
                ui.button("Add", on_click=on_save_cb)
                ui.button("Cancel", on_click=dialog.close)

    return dialog


async def editPolicyDialog():
    policy = {}
    rsp = await BridgeCall(
        "com.novus.ns",
        "/com/novus/ns",
        "com.novus.ns.accounts",
        "GetPasswordPolicy",
        "",
        [],
    )

    if rsp.error_name is not None:
        ui.notify(rsp.error_name)
    else:
        for k, v in rsp.body[0].items():
            policy[k] = v.value

    with ui.dialog() as dialog:

        with ui.card().classes("w-full max-h-[90vh] overflow-y-auto"):
            ui.label("Edit Password Policy").classes("text-h5")

            ui.input("max length").bind_value(policy, "max")
            ui.input("min length").bind_value(policy, "min")
            ui.checkbox("require upper").bind_value(policy, "upper")
            ui.checkbox("require lower").bind_value(policy, "lower")
            ui.checkbox("require symbol").bind_value(policy, "symbol")
            ui.checkbox("require digit").bind_value(policy, "digit")

            async def on_save_cb():
                newPolicy = {
                    "max": Variant("u", policy["max"]),
                    "min": Variant("u", policy["min"]),
                    "upper": Variant("b", policy["upper"]),
                    "lower": Variant("b", policy["lower"]),
                    "symbol": Variant("b", policy["symbol"]),
                    "digit": Variant("b", policy["digit"]),
                }
                rsp = await BridgeCall(
                    "com.novus.ns",
                    "/com/novus/ns",
                    "com.novus.ns.accounts",
                    "SetPasswordPolicy",
                    "a{sv}",
                    [newPolicy],
                )
                if rsp.error_name is not None:
                    ui.notify(rsp.body[0])
                    dialog.close()

            with ui.row():
                ui.button("save", on_click=on_save_cb)
                ui.button("close", on_click=dialog.close)

    return dialog


def deleteUserDialog(username: str):

    with ui.dialog() as dialog:
        with ui.card().classes("w-full max-h-[90vh] overflow-y-auto"):
            ui.label(f"Delete Account").classes("text-h5")
            ui.label(f"Are you sure you want to delete {username}")
            with ui.row():
                ui.button("Cancel", on_click=dialog.close())

                async def on_delete_cb():
                    log.info("CALL delete DBUS")
                    rsp = await BridgeCall(
                        "com.novus.ns",
                        "/com/novus/ns",
                        "com.novus.ns.accounts",
                        "Remove",
                        "s",
                        [username],
                    )
                    if rsp.error_name is not None:
                        ui.notify(rsp.body[0])

                    dialog.submit(f"DELETED!!! {username} RESULTS")

                ui.button("Delete", on_click=on_delete_cb)

    return dialog


usernameValidation = {
    "Username must be at least 5 characters": lambda value: len(value) >= 5,
    "Username must be 24 or less characaters": lambda value: 24 >= len(value),
}


async def validatePass(value):
    rsp = await ValidatePassword(value)
    if rsp.error_name is not None:
        return rsp.body[0]
    else:
        return None


async def AddUser(u: User) -> Message:

    if u.Group == "admin":

        return await BridgeCall(
            "com.novus.ns",
            "/com/novus/ns",
            "com.novus.ns.accounts",
            "AddAdmin",
            "ss",
            [u.Username, u.Password],
        )

    else:
        return await BridgeCall(
            "com.novus.ns",
            "/com/novus/ns",
            "com.novus.ns.accounts",
            "AddUser",
            "ss",
            [u.Username, u.Password],
        )


async def EditUser(u: User) -> Message:
    pass


def validate_group(group: list):
    return [x.validate(return_result=False) for x in group]


async def addUserDialog():
    newUser = User()
    with ui.dialog() as dialog:
        with ui.card().classes("w-full max-h-[90vh] overflow-y-auto"):
            ui.label("Add user").classes("text-h5")

            user = ui.input("username", validation=usernameValidation).bind_value(
                newUser, "Username"
            )

            def mustMatch(v):
                if not v == p1.value:
                    return "passwords must match"
                else:
                    return None

            p1 = ui.input("password", validation=validatePass)

            p2 = ui.input("repeat password", validation=mustMatch).bind_value_to(
                newUser, "Password"
            )

            ui.select(["admin", "user"]).bind_value(newUser, "Group")

            async def on_save_cb():
                if all(validate_group([p1, p2, user])):

                    rsp = await AddUser(newUser)

                    if rsp.error_name is not None:
                        ui.notify(rsp.body[0])
                    else:
                        ui.notify(rsp, type="positive")
                        dialog.close()

                else:
                    ui.notify("Please correct the errors", type="negative")

            with ui.row():
                ui.button("Add", on_click=on_save_cb)
                ui.button("Cancel", on_click=dialog.close)

    return dialog
