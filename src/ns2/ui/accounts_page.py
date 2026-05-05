from nicegui import ui, app

from ns2.lib.accounts_lib import _getUsersAndAdmins, GetUserByName
from ns2.api.dbus import get_dbus
from ns2.ui.accountsDialogs import *


async def accounts_page():
    """user page content"""

    addDialog = addUserDialog()
    # editDialog = editUserDialog()
    # deleteDialog = deleteUserDialog(None)

    accountsTable = (
        ui.table(
            title="Accounts",
            rows=await _getUsersAndAdmins(),
            column_defaults={
                "align": "left",
                "headerClasses": "uppercase text-primary",
            },
        )
        .classes("w-full")
        .props("dense")
    )
    accountsTable.props(f'visible-columns={"Username,Groups"}')  # Only show these
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

    # accountsTable.on("edit-account", editDialog.open)

    async def on_delete_cb(e):
        with deleteUserDialog(e.args) as dialog:
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


async def accounts_user_page(user: str):
    # ui.label("User Configuration").classes("text-h5")
    await account_card(user)


@ui.refreshable
async def edit_card(username: str):
    user: SystemAccount
    # user = awaitGetUserByName(username)

    with ui.card().props("flat"):
        with ui.row():
            ui.link("Accounts", "/accounts").classes("text-accent")
            ui.label(">")
            ui.label(user.UserName)

        with ui.row().classes("w-full justify-between"):
            ui.label(user.UserName).classes("font-bold").classes("text-h5")
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

                ui.label(await GetUsersState(await get_dbus()))

    with ui.card():
        with ui.row().classes("w-full justify-between"):
            ui.label("Authorized public SSH keys").classes("text-h5 font-bold")
            with ui.row():
                ui.button("Terminate session")


@ui.refreshable
async def new_card():
    user = SystemAccount()
    user.UserName = "New User"


@ui.refreshable
async def account_card(username: str):

    if username == "create-new-user":

        await new_card()
    # else:

    # await edit_card(username)
