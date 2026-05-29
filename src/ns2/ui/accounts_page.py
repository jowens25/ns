from nicegui import ui
from dbus_next import Message
from ns2.lib.accounts import GetUsers, SystemAccount
from ns2.lib.bridge import GetBridge, BridgeCall
from ns2.ui.accountsDialogs import (
    addUserDialog,
    deleteUserDialog,
    editUserDialog,
    editPolicyDialog,
)


from ns2.utils import log


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
async def accounts_table():

    addDialog = await addUserDialog()
    policyDialog = await editPolicyDialog()

    rsp = await GetUsers()

    if rsp.error_name is not None:
        ui.notify(rsp.error_name)
        ui.label(rsp.error_name)
        return
    accountsTable = (
        ui.table(
            title="Accounts",
            rows=rsp.body[0],
            column_defaults={
                "align": "left",
                "headerClasses": "uppercase text-primary",
            },
        )
        .classes("w-full")
        .props("dense")
    )
    # accountsTable.props(f"visible-columns={'Username,Groups,login'}")  # Only show these
    accountsTable.add_slot(
        "header",
        r"""
          <q-tr :props="props">
             <q-th v-for="col in props.cols" :key="col.name" :props="props"> {{ col.label }} </q-th>
              <q-th auto-width />
          </q-tr>
      """,
    )

    with accountsTable.add_slot("top-right"):
        with ui.row():
            ui.input("Search").bind_value(accountsTable, "filter").props("dense")

            ui.button(icon="add", on_click=addDialog.open).props("color=accent")

            ui.button(icon="settings", on_click=policyDialog.open).props("color=accent")

    # accountsTable.on("edit-account", editDialog.open)

    async def on_delete_cb(e):
        username: str = e.args
        with deleteUserDialog(username) as dialog:
            result = await dialog
            ui.notify(result)

    async def on_edit_cb(e):
        with editUserDialog(e.args) as dialog:
            result = await dialog
            ui.notify(result)

    accountsTable.on("delete-account", on_delete_cb)

    accountsTable.on("edit-account", on_edit_cb)

    accountsTable.add_slot(
        "body",
        r"""
        <q-tr :props="props">
            <!-- normal columns with special handling for Username -->
            <q-td v-for="col in props.cols" :key="col.name" :props="props">
                <template v-if="col.name === 'Username'">
                    <a :href="'/accounts/' + props.row.Username"
                       class="text-accent cursor-pointer hover:underline">
                        {{ col.value }}
                    </a>
                </template>
                <template v-else>
                    {{ col.value }}
                </template>
            </q-td>
            <!-- 3-dot menu -->
            <q-td auto-width>
                <q-btn flat round dense icon="more_vert" color="accent">
                    <q-menu auto-close>
                        <q-list style="min-width: 150px">

                            <q-item clickable
                                @click="$parent.$emit('edit-account', props.row.Username)">
                                <q-item-section class="text-negative">
                                    Edit account
                                </q-item-section>
                            </q-item>

                            <q-item clickable
                                @click="$parent.$emit('delete-account', props.row.Username)">
                                <q-item-section class="text-negative">
                                    Delete account
                                </q-item-section>
                            </q-item>

                        </q-list>
                    </q-menu>
                </q-btn>
            </q-td>
        </q-tr>
        """,
    )


async def accounts_page():
    """user page content"""

    await SetupNotifications()

    await accounts_table()

    # editDialog = editUserDialog()
    # deleteDialog = deleteUserDialog(None)


async def accounts_user_page(user: str):
    # ui.label("User Configuration").classes("text-h5")
    await account_card(user)


@ui.refreshable
async def edit_card(username: str):
    user = SystemAccount()
    # user = awaitGetUserByName(username)

    with ui.card().props("flat"):
        with ui.row():
            ui.link("Accounts", "/accounts").classes("text-accent")
            ui.label(">")
            ui.label(user.Username)

        with ui.row().classes("w-full justify-between"):
            ui.label(user.Username).classes("font-bold").classes("text-h5")
            with ui.row():
                ui.button("Terminate session")
                ui.button("Delete")

        ui.separator()

        with ui.column().classes("flex-1 gap-4"):
            with ui.row().classes("flex-1"):
                ui.label("Full name").classes("font-bold w-32")
                ui.input().bind_value(user, "UserInfo").props("dense")

            with ui.row().classes("flex-1"):
                ui.label("User name").classes("font-bold w-32")
                ui.label().bind_text_from(user, "UserName").props("dense")

            with ui.row().classes("flex-1"):
                ui.label("Groups").classes("font-bold w-32")
                with ui.row().classes("flex-1 flex-wrap").props("dense"):
                    for g in user.Groups.split(", "):
                        ui.chip(g, removable=True).props("dense")

            with ui.row().classes("flex-1"):
                ui.label("Last login").classes("font-bold w-32")

            with ui.row().classes("flex-1"):
                ui.label("Options").classes("font-bold w-32")
                ui.link("edit").classes("text-accent")

            # with ui.row().classes("flex-1 gap-32"):
            with ui.row().classes("items-center justify-start w-full"):
                ui.label("Password").classes("font-bold w-32")
                ui.button("Set password").props("dense")
                ui.button("Force change").props("flat dense")
                ui.label("this should get its value from ")
                ui.link("edit").classes("text-accent")

            with ui.row().classes("flex-1"):
                ui.label("Home directory").classes("font-bold w-32")
                ui.label().bind_text_from(user, "HomeDir")

            with ui.row().classes("flex-1"):
                ui.label("Shell").classes("font-bold w-32")
                ui.label().bind_text_from(user, "Shell")
                ui.link("change").classes("text-accent")

                # ui.label(await GetUsersState(await get_dbus()))

    with ui.card():
        with ui.row().classes("w-full justify-between"):
            ui.label("Authorized public SSH keys").classes("text-h5 font-bold")
            with ui.row():
                ui.button("Terminate session")


@ui.refreshable
async def new_card():
    user = SystemAccount()
    user.UserName = "New User"

    ui.button("test")


@ui.refreshable
async def account_card(username: str):

    await new_card()

    if username == "create-new-user":
        await new_card()
    # else:

    # await edit_card(username)
