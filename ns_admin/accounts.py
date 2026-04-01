from nicegui import ui, app

from ns_admin.accounts_lib import *
from ns_admin.dbus import get_dbus


async def accounts_page():
    """user page content"""

    ui.label("User Configuration").classes("text-h5")

    # table("Groups", GetCombinedDict(), "Name", add_group_dialog(), "Name,Id,NumLocalUsers,LocalUsers")  # Only show these
    # ui.table("Groups", , "Name", add_group_dialog(), "Name,PrimaryId,SecondaryId,Info,Home,Shell")  # Only show these

    group = SystemGroup()

    with ui.dialog() as asGroupDialog:
        with ui.card():
            ui.label("Create new group")
            errorLabel = ui.label()
            ui.input("name").bind_value(group, "GroupName")
            ui.input("id").bind_value(group, "GID")
            with ui.row():

                async def on_save_cb():
                    if group.GroupName != None and group.GID != None:
                        print(group)

                        ui.notify(addGroup(group.GroupName, group.GID))
                        # if all(validate_group([version, username, permissions, auth_type, auth_pass, priv_type, priv_pass])):
                        #    print(asdict(v3))

                        # snmp = await GetSnmp(AppBus)
                        # rsp = await snmp.call_create_v3_user(asdict(v3))
                        # rsp = await AddV3User(AppBus, asdict(v3))
                        # print(rsp)
                        # await groupsTable.refresh()
                        asGroupDialog.close()
                    else:
                        errorLabel.value = "Please correct the errors"

                        ui.notify("Please correct the errors")

                def on_cancel_cb():
                    asGroupDialog.close()

                ui.button("create", on_click=on_save_cb).props(
                    "color=accent align=center"
                )
                ui.button("cancel").props("flat color=accent dense align=center")

    with ui.expansion("Groups", icon="groups").classes("w-full") as expansion:
        with expansion.add_slot("body"):
            ui.button("test")
        groupsTable = (
            ui.table(
                title="Groups",
                rows=GetCombinedGroupDict(),
                column_defaults={
                    "align": "left",
                    "headerClasses": "uppercase text-primary",
                },
            )
            .classes("w-full")
            .props("dense")
        )

        # groupsTable.add_slot(
        #    f"body-cell-Accounts",
        #    f""" <q-td :props="props">
        #                  <a :href="'/accounts/'+ props.row.GroupName" class="text-accent cursor-pointer hover:underline"> {{{{ props.value }}}} </a>
        #                  </q-td> """,
        # )

        # with groupsTable.add_slot("body-cell-Accounts"):
        #    with groupsTable.cell("link"):
        #        ui.link().props(":href=props.value :innerHTML=props.value").classes(
        #            "text-accent"
        #        )

        groupsTable.add_slot(
            "body-cell-Accounts",
            """
        <q-td :props="props">
            <span v-for="(account, index) in props.value" :key="index">
                <span v-if="index > 0">, </span>
                <a v-if="account.link" 
                   :href="'/accounts/' + account.name" 
                   class="text-accent cursor-pointer hover:underline">
                    {{ account.name }}
                </a>
                <span v-else>{{ account.name }}</span>
            </span>
        </q-td>
        """,
        )

        # Name: Optional[str] = None
        # Id: Optional[str] = None
        # NumLocalUsers: Optional[str] = None
        # LocalUsers:

        groupsTable.props(
            f'visible-columns={"GroupName,GID,NumberOfUsers,Accounts"}'
        )  # Only show these

        with groupsTable.add_slot("top-right"):
            with ui.row():
                groupFilter = (
                    ui.input("Search for group")
                    .bind_value(groupsTable, "filter")
                    .props("align=center dense")
                )

                ui.button(
                    "Create new group", icon="add", on_click=asGroupDialog.open
                ).props("flat color=accent dense align=center")

    with ui.expansion("Accounts", icon="account_box", value=True).classes("w-full"):

        ui.button(
            "Create new account",
            on_click=lambda e: ui.navigate.to("accounts/create-new-user"),
        )

        accountsTable = (
            ui.table(
                title="Accounts",
                rows=GetCombinedAccountDict(),
                column_defaults={
                    "align": "left",
                    "headerClasses": "uppercase text-primary",
                },
            )
            .classes("w-full")
            .props("dense")
        )

        accountsTable.props(
            f'visible-columns={"UserName,UID,Groups"}'
        )  # Only show these

        accountsTable.add_slot(
            "header",
            r"""
              <q-tr :props="props">
                 <q-th v-for="col in props.cols" :key="col.name" :props="props"> {{ col.label }} </q-th>
                  <q-th auto-width />
              </q-tr>
          """,
        )

        async def handle_remove_service(e, zone="test"):
            print("delete: ", e.args)
            pass
            # rsp = await removeServiceFromZone(zone, e.args)
            # await zoneServicesTable.refresh()

            # ui.notify(rsp)

        accountsTable.on("remove-service", handle_remove_service)

        accountsTable.add_slot(
            "body",
            r"""
            <q-tr :props="props">
                <!-- normal columns with special handling for UserName -->
                <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    <template v-if="col.name === 'UserName'">
                        <a :href="'/accounts/' + props.row.UserName" 
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
                                    @click="$parent.$emit('remove-service', props.row.UserName)">
                                    <q-item-section class="text-negative">
                                        Edit user
                                    </q-item-section>
                                </q-item>  
                                
                            
                                <q-item clickable
                                    @click="$parent.$emit('remove-service', props.row.UserName)">
                                    <q-item-section class="text-negative">
                                        Log user out
                                    </q-item-section>
                                </q-item>
                                
                                <q-item clickable
                                    @click="$parent.$emit('remove-service', props.row.UserName)">
                                    <q-item-section class="text-negative">
                                        Lock account
                                    </q-item-section>
                                </q-item>  
                                
                                <q-item clickable
                                    @click="$parent.$emit('remove-service', props.row.UserName)">
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
    user = GetUserByName(username)

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
    else:

        await edit_card(username)
