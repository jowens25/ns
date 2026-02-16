from ns2.systemd import *

from nicegui import ui, app
from dataclasses import dataclass, asdict

from ns2.dbus import get_dbus

from typing import Optional

from ns2.snmp import snmp_call, V3User, V2User, snmp_config_file, default_persistent_dir_path

from ns2.snmp import *

sourceValidation = {"Please enter a valid ip address, network or default": lambda value: len(value) > 0}
passphraseValidation = {"Passphrase must be at least 8 characters": lambda value: len(value) >= 8,  
                        "Passphrase must be 24 or less characaters": lambda value: 24 >= len(value)}
usernameValidation = {"Username must be at least 5 characters": lambda value: len(value) >= 5, 
                      "Username must be 24 or less characaters": lambda value: 24 >= len(value)}

def validate_group(group: list):
    return [x.validate() for x in group]
    

async def create_v3_user_dialog():
    AppBus = await get_dbus()
    with ui.dialog() as createV3Dialog:
        v3 = V3User()
        with ui.card().classes("w-full"):
            with ui.column().classes("w-full"):
                version = ui.input(label="Version").classes("w-full").bind_value(v3, "Version")
                version.disable()
                username = ui.input(label="Username", validation=usernameValidation).classes("w-full").bind_value(v3, "UserName")
                permissions = ui.select(label="Permissions", options=["roprivgroup", "rwprivgroup"]).classes("w-full").bind_value(v3, "Permissions")
                auth_type = ui.select(label="Auth Alg", options=['SHA', 'MD5']).classes("w-full").bind_value(v3, "AuthType")
                auth_pass = ui.input(label="Auth Passphrase", validation=passphraseValidation).classes("w-full").bind_value(v3, "AuthPassphrase")
                priv_type = ui.select(label="Priv Alg", options=["AES", "DES"]).classes("w-full").bind_value(v3, "PrivType")
                priv_pass = ui.input(label="Auth Passphrase", validation=passphraseValidation).classes("w-full").bind_value(v3, "PrivPassphrase")
                with ui.row().classes("items-center justify-between gap-4 w-full"):
                    
                    async def on_save_cb():
                        if all(validate_group([version, username, permissions, auth_type, auth_pass, priv_type, priv_pass])):
                            print(asdict(v3))
                            
                            #snmp = await GetSnmp(AppBus)
                            #rsp = await snmp.call_create_v3_user(asdict(v3))
                            rsp = await AddV3User(AppBus, asdict(v3))
                            print(rsp)
                            await v3table.refresh()
                            createV3Dialog.close()
                        else:
                            ui.notify("Please correct the errors", type='negative')

                    def on_cancel_cb():
                        createV3Dialog.close()

                    ui.button("save", on_click=on_save_cb).props("flat color=accent align=left") 
                    ui.button(icon="cancel", on_click=on_cancel_cb).props("flat color=accent align=left")
    
    return createV3Dialog     


@ui.refreshable
async def v3table():
    AppBus = await get_dbus()

    #snmp = await GetSnmp(AppBus)
    #v3Users = await snmp.call_get_v3_users()
    v3Users = await ReadV3Users()
    #print(v3Users)
    createV3Dialog = await create_v3_user_dialog()
    
    table = ui.table(
            title="v3 Users",
            rows=v3Users,
            column_defaults={
                "align": "left",
                "headerClasses": "uppercase text-primary",
            },
        ).classes("w-full")
    
    table.add_slot(f'body-cell-UserName', f''' <q-td :props="props">
                   <a :href="'/snmp/v3/'+ props.row.UserName" class="text-accent cursor-pointer hover:underline"> {{{{ props.value }}}} </a>
                   </q-td> ''')

    table.props(f'visible-columns={"UserName,Version,GroupName,AuthType,PrivType"}')  # Only show these
    
    with table.add_slot('top-right'):
        ui.button(icon="add", on_click = createV3Dialog.open).props(
            "flat color=accent align=left").classes("w-full").props("dense")
    




@ui.refreshable
async def v2table():
    AppBus = await get_dbus()
    snmp = await GetSnmp(AppBus)
    #v2Users = await snmp.call_get_v2_users()
    v2Users = await ReadV2Users()
    
    with ui.dialog() as createV2Dialog:
        v2 = V2User()
        v2.Version = "v2c"
        v2.Permissions = "rwnoauthgroup"
        v2.Source = "default"
        with ui.card().classes("w-full"):
            with ui.column().classes("w-full"):
                version = ui.select(label="Version", options=["v2c", "v1"]).classes("w-full").bind_value(v2, "Version")
                permissions = ui.select(label="Permissions", options=['rwnoauthgroup', 'ronoauthgroup']).classes("w-full").bind_value(v2, "Permissions")
                community = ui.input("Community", 
                                     validation={'Community required': lambda value: len(value) > 0}).classes("w-full").bind_value(v2, "Community")
                source = ui.input("Source / IP Address", 
                                  validation=sourceValidation).classes("w-full").bind_value(v2, "Source")
                with ui.row().classes("items-center justify-between gap-4 w-full"):

                    async def on_save_cb():
                        if all(validate_group([version, permissions, community, source])):
                            #await snmp.call_create_v2_user(asdict(v2))
                            await AddV2User(AppBus, asdict(v2))
                            await v2table.refresh()
                            createV2Dialog.close()
                        else:
                            ui.notify("Please correct the errors", type='negative')
                        
                    def on_cancel_cb():
                        createV2Dialog.close()
                    ui.button("save", on_click=on_save_cb).props("flat color=accent align=left") 
                    ui.button(icon="cancel", on_click=on_cancel_cb).props("flat color=accent align=left")

    table = ui.table(
            title="v2 Users",
            rows=v2Users,
            column_defaults={
                "align": "left",
                "headerClasses": "uppercase text-primary",
            },
        ).classes("w-full")
    
    table.add_slot(f'body-cell-Community', f'''
            <q-td :props="props">
                <a :href="'/snmp/v2/'+ props.row.Community" class="text-accent cursor-pointer hover:underline"> {{{{ props.value }}}} </a>
            </q-td>
        ''')

    table.props(f'visible-columns={"Community,Version,Source,GroupName"}')  # Only show these
    
    with table.add_slot('top-right'):
        ui.button(icon="add", on_click = createV2Dialog.open).props(
            "flat color=accent align=left").classes("w-full").props("dense")
        

    
async def snmp_status():
    AppBus = await get_dbus()

    with ui.column() as status:
        ui.label("SNMP").classes("text-h5")
        
        async def snmp_switch_cb(e):
            action = "enable" if  e.sender.value else "disable"
            with ui.dialog() as dialog, ui.card():
                ui.label(f'Are you sure you want to {action} snmp?')
                with ui.row():
                    ui.button('Cancel', on_click=lambda: dialog.submit("Cancel")).props("flat color=accent align=left")
                    ui.button(f'{action}', on_click=lambda: dialog.submit(action)).props("flat color=accent align=left")
        
            result = await dialog
            active = await isActive(AppBus, 'snmpd.service')
            
            
            if result == "enable" and not active:
                await systemd_start(AppBus, 'snmpd.service')
            
            if result == "disable" and active:
                await systemd_stop(AppBus, 'snmpd.service')


            e.sender.value = await isActive(AppBus, 'snmpd.service')

        async def snmp_reset_cb(e):
            with ui.dialog() as dialog, ui.card():
                ui.label(f'Are you sure you want to reset snmp?')
                with ui.row():
                    ui.button('Cancel', on_click=lambda: dialog.submit("Cancel")).props("flat color=accent align=left")
                    ui.button('Reset', on_click=lambda: dialog.submit("reset")).props("flat color=accent align=left")    
            if await dialog == "reset":
                
                #snmp = await GetSnmp(AppBus)
                #await snmp.call_reset()
                await ResetSnmpd()
                v2table.refresh()
                v3table.refresh()
            
        
        with ui.card().classes("w-full"):
            snmp_service_switch = ui.switch("SNMPD Status").on('click', lambda e: snmp_switch_cb(e)).props("flat color=accent align=left dense")
            snmp_service_switch.value = await isActive(AppBus, 'snmpd.service')
            ui.button("Reset SNMPD Config", on_click=snmp_reset_cb).props("flat color=accent align=left dense")
    
    return status

async def snmp_page():
    
    #def props_cb(interface_name, changed_properties, invalidated_properties):
    #    print("props ch cb")
    #    #print(changed_properties['ActiveState'])
    #    status.update()
    #    
    #print("registered")
    #snmpDaemon = await getUnitInterface(dbus.AppBus, "snmpd.service")
    #snmpDaemon.on_properties_changed(props_cb)

   
    await snmp_status()
    await v2table()  # Only show these
    await v3table()
        


async def snmp_user_page(version :str, user: str):
    with ui.row():
        ui.link('SNMP', '/snmp')
        ui.label('>')
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
    AppBus = await get_dbus()

    snmp = await GetSnmp(AppBus)
    #user = await snmp.call_get_v2_user_by_community(community)
    user = await ReadV2UserByCommunity(community)
    v2User = V2User(**user)
    with ui.card().classes("w-full"):
        with ui.column().classes("w-full"):
            version = ui.select(label="Version", options=["v2c", "v1"]).classes("w-full").bind_value(v2User, "Version")
            permissions = ui.select(label="Permissions", options=['rwnoauthgroup', 'ronoauthgroup']).classes("w-full").bind_value(v2User, "Permissions")
            community = ui.input("Community", validation={'Community required': lambda value: len(value) > 0}).classes("w-full").bind_value(v2User, "Community")
            source = ui.input("Source / IP Address", validation=sourceValidation).classes("w-full").bind_value(v2User, "Source")
            with ui.row().classes("items-center justify-between gap-4 w-full"):

                async def on_save_cb():
                    disable_group(group)
                    save_button.enabled = False
                    edit_button.enabled = True
                    #await snmp.call_modify_v2_user(asdict(v2User))
                    await EditV2User(AppBus, asdict(v2User))
                    await v2table.refresh()
                    ui.navigate.back()

                def on_edit_cb():
                    enable_group(group)
                    edit_button.enabled = False
                    save_button.enabled = True

                async def on_delete_cb():
                    with ui.dialog() as dialog, ui.card():
                        ui.label(f'Are you sure you want to delete {v2User.Community}?')
                        with ui.row():
                            ui.button('Yes', on_click=lambda: dialog.submit(True)).props("flat color=accent align=left")
                            ui.button('No', on_click=lambda: dialog.submit(False)).props("flat color=accent align=left")
                    result = await dialog
                    if result:
                        #await snmp.call_remove_v2_user(asdict(v2User))
                        await DeleteV2User(AppBus, asdict(v2User))
                        v2table.refresh()
                        ui.navigate.back()
                        ui.notify(f'User {v2User.Community} deleted...')
                    else:
                        dialog.close()

                edit_button = ui.button("edit", on_click= on_edit_cb).props("flat color=accent align=left")
                save_button = ui.button("save", on_click= on_save_cb).props("flat color=accent align=left") 
                delete_button = ui.button(icon="delete", on_click=on_delete_cb).props("flat color=accent align=left")

                group = [community, source, version, permissions]

                disable_group(group)
                edit_button.enabled = True
                save_button.enabled = False
    




    
async def edit_delete_v3_user_card(username):
    AppBus = await get_dbus()

    snmp = await GetSnmp(AppBus)
    #userData = await snmp.call_get_v3_user_by_username(username)
    userData = await ReadV3UserByUsername(username)
    initUser = V3User(**userData)
    finalUser = V3User(**userData)

    with ui.card().classes("w-full"):
        with ui.column().classes("w-full"):
    
            version = ui.input(label="Version").classes("w-full").bind_value(finalUser, "Version")
            version.disable()
            username = ui.input(label="Username", validation=usernameValidation).classes("w-full").bind_value(finalUser, "UserName")
            permissions = ui.select(label="Permissions", options=["roprivgroup", "rwprivgroup"]).classes("w-full").bind_value(finalUser, "Permissions")
            auth_type = ui.select(label="Auth Alg", options=['SHA', 'MD5']).classes("w-full").bind_value(finalUser, "AuthType")
            auth_pass = ui.input(label="Auth Passphrase", validation=passphraseValidation).classes("w-full").bind_value(finalUser, "AuthPassphrase")
            priv_type = ui.select(label="Priv Alg", options=["AES", "DES"]).classes("w-full").bind_value(finalUser, "PrivType")
            priv_pass = ui.input(label="Auth Passphrase", validation=passphraseValidation).classes("w-full").bind_value(finalUser, "PrivPassphrase")

            with ui.row().classes("items-center justify-between gap-4 w-full"):

                async def on_save_cb():
                        disable_group(group)
                        save_button.enabled = False
                        edit_button.enabled = True
                        if all(validate_group([version, username, permissions, auth_type, auth_pass, priv_type, priv_pass])):
                            #await snmp.call_modify_v3_user(asdict(initUser), asdict(finalUser))
                            await EditV3User(asdict(initUser), asdict(finalUser))
                            ui.navigate.back()
                        else:
                            ui.notify("Please correct the errors", type='negative')


                def on_edit_cb():
                    enable_group(group)
                    edit_button.enabled = False
                    save_button.enabled = True


                async def on_delete_cb():
                    with ui.dialog() as dialog, ui.card():
                        ui.label(f'Are you sure you want to delete {initUser.UserName}?')
                        with ui.row():
                            ui.button('Yes', on_click=lambda: dialog.submit(True)).props("flat color=accent align=left")
                            ui.button('No', on_click=lambda: dialog.submit(False)).props("flat color=accent align=left")
                    result = await dialog
                    if result:
                        #await snmp.call_remove_v3_user(asdict(initUser))
                        await DeleteV3User(AppBus, asdict(initUser))
                        ui.navigate.back()
                        ui.notify(f'User {initUser.UserName} deleted...')
                    else:
                        dialog.close()

                edit_button = ui.button("edit", on_click= on_edit_cb).props("flat color=accent align=left")
                save_button = ui.button("save", on_click= on_save_cb).props("flat color=accent align=left") 
                delete_button = ui.button(icon="delete", on_click=on_delete_cb).props("flat color=accent align=left")

                group = [permissions, username, auth_type,auth_pass,priv_type,priv_pass]

                disable_group(group)
                edit_button.enabled = True
                save_button.enabled = False


