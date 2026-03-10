from nicegui import ui, app

from ns_admin.accounts_lib import *


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

    with ui.expansion("Groups", icon="groups").classes("w-full"):
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
        data = GetCombinedAccountDict()
        print(data)
        accountsTable = (
            ui.table(
                title="Accounts",
                rows=data,
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
async def account_card(user: str):

    with ui.card().props("flat"):
        with ui.row():
            ui.link("Networking", "/networking").classes("text-accent")
            ui.label(">")
            ui.label(user)

            with ui.row().classes("w-full items-center justify-between"):
                ui.label(user).classes("font-bold").classes("text-h5")
                ui.button("Terminate session").props("color=accent align right")
                ui.button("Delete").props("color=accent align=right")
            # ui.label().classes("text-h6").bind_text(interface, "Name")
            # ui.label().classes("text-h6").bind_text(interface, "HardwareAddress")
            # async def connection_sw_cb(e):
            #    action = "enable" if e.sender.value else "disable"
            #    with ui.dialog() as dialog, ui.card():
            #        ui.label(f"Are you sure you want to {action} this connection?")
            #        with ui.row():
            #            ui.button(
            #                "Cancel", on_click=lambda: dialog.submit("Cancel")
            #            ).props("flat color=accent align=left")
            #            ui.button(
            #                f"{action}", on_click=lambda: dialog.submit(action)
            #            ).props("flat color=accent align=left")
            #    result = await dialog
            #    if result == "enable":
            #        await nm.call_activate_connection("/", interface._dev_path, "/")
            #    elif result == "disable":
            #        await nm.call_deactivate_connection(interface._act_con_path)
            #    else:
            #        print('canceled')
            #
            #    interface_card.refresh()

        #            ui.switch("Connected").on("click", lambda e: connection_sw_cb(e)).props(
        #                "flat color=accent"
        #            ).bind_value_from(interface, "Active")
        ui.separator()
        #
        #    #ui.spinner(size='lg').bind_visibility_from(interface, "Active", backward=lambda e: (not e))

        #
        with ui.column().classes("flex-1 gap-4"):
            with ui.row().classes("flex-1 gap-32"):
                ui.label("Full name").classes("font-bold w-32")
                # ui.label().bind_text_from(interface, "Status")
                ui.label("test")
            with ui.row().classes("flex-1 gap-32"):
                ui.label("User name").classes("font-bold w-32")
                # ui.label().bind_text_from(interface, "StateString")
            with ui.row().classes("flex-1 gap-32"):
                ui.label("Groups").classes("font-bold w-32")

            with ui.row().classes("flex-1 gap-32"):
                ui.label("Last login").classes("font-bold w-32")

            with ui.row().classes("flex-1 gap-32"):
                ui.label("Options").classes("font-bold w-32")

            with ui.row().classes("flex-1 gap-32"):
                ui.label("Password").classes("font-bold w-32")

            with ui.row().classes("flex-1 gap-32"):
                ui.label("Home directory").classes("font-bold w-32")

            with ui.row().classes("flex-1 gap-32"):
                ui.label("Shell").classes("font-bold w-32")

                # ui.label().bind_text_from(interface, "Carrier")
            # with ui.row().classes("flex-1 gap-16"):


#            ui.label("General").classes("font-bold w-8")
#            async def auto_connect_cb(e):
#                return
#                device = GetDevice(dbus.Bus, interface._dev_path)
#                settings = await GetSettings(device)
#                settings["connection"]["autoconnect"] = Variant(
#                    "b", e.value
#                )
#                # await connection.call_update2(settings, 0x1, {})
#                # await device.call_reapply(settings, 0, 0)
#            ui.checkbox(
#                "Connect automatically", on_change=auto_connect_cb
#            ).props("flat color=accent dense").bind_value(
#                interface, "AutoConnect"
#            )
#
#
#        with ui.row().classes("flex-1 gap-16"):
#            ui.label("IPv4").classes("font-bold w-8")
#            ui.label().bind_text_from(interface, "Ip4")
#            ui.label("Edit").classes(
#                "text-accent cursor-pointer hover:underline"
#            ).on("click", lambda: edit_ip_connection('ipv4', device))
#
#
#        with ui.row().classes("flex-1 gap-16"):
#            ui.label("IPv6").classes("font-bold w-8")
#            ui.label().bind_text_from(interface, "Ip6")
#            ui.label("Edit").classes(
#                "text-accent cursor-pointer hover:underline"
#            ).on("click", lambda: edit_ip_connection('ipv6', device))
