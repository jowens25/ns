from nicegui import ui, app, binding
from ns2.networking import *
from ns2.firewalld import *
from dbus_next.signature import Variant
from dbus_next.errors import DBusError
from dbus_next.aio.proxy_object import ProxyInterface
from ns2.dbus import get_dbus

from ns2.systemd import *



#async def service_list(services: dict):
#    for s in await getServices(AppBus):
#        with ui.row():
#            ui.checkbox(s).props("flat color=accent align=left").bind_value(services, s)
#
#            with ui.column():
#                ui.label().bind_text_from(s, "UDP")
#                ui.label().bind_text_from(s, "TCP")


@ui.refreshable
async def firewall_status(on_network_page: bool):
    AppBus = await get_dbus()
    
    zoneDialog = await addZoneDialog()

    print("FIREWALL STATUS")
    firewallInfo = FirewallInfo()
    firewallInfo.Enable = await isActive(AppBus, 'firewalld.service')
    firewallInfo.Status = (await getServiceState(AppBus, "firewalld.service")).capitalize()
    numActiveZones = 0
    if firewallInfo.Enable:
        numActiveZones = len(await GetZones(AppBus))
        
    
    with ui.column().classes("w-full"):
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes( "items-center"):
                ui.label("Firewall").classes("text-h6")
                if on_network_page:
                    ui.link(f'{numActiveZones} active zones', '/networking/firewall').classes('text-accent')
            
                async def fire_switch_cb(e):
                    action = "enable" if  e.sender.value else "disable"
                    with ui.dialog() as dialog, ui.card():
                        ui.label(f'Are you sure you want to {action} firewalld?')
                        with ui.row():
                            ui.button('Cancel', on_click=lambda: dialog.submit("Cancel")).props("flat color=accent align=left")
                            ui.button(f'{action}', on_click=lambda: dialog.submit(action)).props("flat color=accent align=left")
                    result = await dialog
                    active = await isActive(AppBus, "firewalld.service")
                    if result == "enable" and not active:
                        await systemd_start(AppBus, "firewalld.service")
                    if result == "disable" and active:
                        await systemd_stop(AppBus, "firewalld.service")
                    await firewall_status.refresh()

                ui.switch(f"Status: {firewallInfo.Status}").on('click', lambda e: fire_switch_cb(e)
                        ).props("flat color=accent align=left dense").bind_value(firewallInfo, "Enable").bind_text

            if on_network_page:
                ui.button("Edit rules and zones", on_click=lambda e: ui.navigate.to('/networking/firewall')).props("flat color=accent align=left dense")

            else:
                ui.label("LABEL")
                ui.button("add new zone", on_click=zoneDialog.open).props("color=accent align=left")
        

 


    
    
def InterfaceText(zoneSettings :ZoneInfo):
    interfaces = zoneSettings.Interfaces
    if len(interfaces) == 1:
        l1 = ui.label("Interface:").classes("font-bold")
    else:
        l1= ui.label("Interfaces:").classes("font-bold")
    l2 = ui.label(formatListToString(interfaces))
    return (l1, l2)

def AllowedAddressText(zoneSettings :ZoneInfo):
    sources = zoneSettings.Sources
    l1 = ui.label("Allowed Addresses:").classes("font-bold")
    if len(sources) == 0:
        l2 = ui.label("Entire subnet")
    else:
        l2 = ui.label(formatListToString(sources))
    return (l1, l2)




async def removeServiceFromZone(zoneName: str, serviceName:str):
    AppBus = await get_dbus()

    print(f'remove {serviceName} from {zoneName}')
    zone = await GetFirewalldZone(AppBus)
    
    res = await zone.call_remove_service(zoneName, serviceName)
    print("res1: ", res)
    conf = await GetFirewalldConfig(AppBus)
    
    p = await conf.call_get_zone_by_name(zoneName)
    
    print(p)
    
    configZone = await GetFirewalldConfigZone(AppBus, p)
    res = await configZone.call_remove_service(serviceName)
    print(res)
    return



async def addZoneDialog():
    AppBus = await get_dbus()

    with ui.dialog() as dialog:
        with ui.card().props('flat'):
            ui.label("Add zone").classes("text-h5")
            ui.label("Interfaces").classes("text-h6")

            with ui.row():
                interfaces = {}
                for i in await GetInterfaces(AppBus):
                    interfaces[i] = False
                    ui.checkbox(i).props("flat color=accent align=left").bind_value(interfaces, i)

            #selectedServices = ui.input_chips('Allowed services', new_value_mode='add-unique', clearable=True).props('disable-input')
            with ui.scroll_area():
                services = formatServicesInRows(await getServicesInfo(AppBus))
                services_table = ui.table(
                        rows=services,
                        column_defaults={
                            "align": "left",
                            "headerClasses": "uppercase text-primary",
                        },
                        row_key='Service',
                        selection='multiple',
                        #on_select=lambda e: print(f'selected: {e.selection}'),                   
                          ).props('dense')
                
              

                services_table.props(f'visible-columns=["Service","UDP","TCP"]')
#
                services_table.add_slot('header', r'''
                    <q-tr :props="props">
                        <q-th auto-width />
                        <q-th auto-width />

                        <q-th v-for="col in props.cols" :key="col.name" :props="props"> {{ col.label }} </q-th>
                    </q-tr>
                ''')
#
                services_table.add_slot('body', r'''
                    <q-tr :props="props">
                                <!-- selection checkbox -->
            <q-td auto-width>
                <q-checkbox 
                    :model-value="props.selected" 
                    @update:model-value="props.selected = !props.selected"
                    color="accent"
                    dense 
                />
            </q-td>

                        <!-- expand button -->
                        <q-td auto-width @click.stop="">
                            <q-btn size="sm" color="accent" round dense 
                                   @click="props.expand = !props.expand" 
                                   :icon="props.expand ? 'remove' : 'add'" />
                        </q-td>
                        <!-- normal columns -->
                        <q-td v-for="col in props.cols" :key="col.name" :props="props" 
                              style="white-space: normal; word-wrap: break-word; overflow-wrap: break-word; max-width: 200px;">
                            {{ col.value }}
                        </q-td>                 
                    </q-tr>
                    <!-- expanded description -->
                    <q-tr v-show="props.expand" :props="props">
                        <q-td colspan="100%" style="max-width: 0;">
                            <div class="text-left"
                                 style="word-wrap: break-word; overflow-wrap: break-word; white-space: normal;">
                                {{ props.row.Description }}
                            </div>
                        </q-td>
                    </q-tr>
                ''')
#
            serviceFilter = ui.input('Search for services').bind_value(services_table, "filter")

            def on_save_cb():
                for c,v in interfaces.items():
                    print(c, v)

                # Get selected services when saving
                selected = [row['Service'] for row in services if row.get('Select', False)]
                print(f"Selected services: {selected}")
            
            with ui.row():
                ui.button('Add zone', on_click=on_save_cb).props("color=accent align=left")
                ui.button('Cancel', on_click=dialog.close).props("flat color=accent align=left")

    return dialog

async def addServiceDialog():
    with ui.dialog() as dialog:
        with ui.card():
            ui.label("nothing")
            ui.button('close', on_click=dialog.close)
        
    return dialog






async def zone_list(firewall):
    with ui.column():
        for zoneName, zoneSetting in firewall.ZoneInfos.items():
            with ui.card().classes("w-full").props('flat').classes("bg-secondary"):
                with ui.column():
                    with ui.row().classes("w-full items-baseline justify-between"):
                        with ui.row().classes("items-baseline"):
                            ui.label(f'{zoneName.capitalize()} zone')
                            InterfaceText(zoneSetting)
                            
                        with ui.row():
                            AllowedAddressText(zoneSetting)
                            
                        with ui.row():
                            addDialog = await addServiceDialog()
                            ui.button("add services", on_click=addDialog.open).props("color=accent align=left")
                            ui.button(icon="more_vert").props("flat color=accent align=left")
                    
                    services = formatServicesInRows(firewall.ZoneInfos[zoneName].ServiceSettings)
                    
                    service_table = ui.table(
                        rows=services,
                        column_defaults={
                            "align": "left",
                            "headerClasses": "uppercase text-primary",
                        },
                        row_key='Service'
                    ).props("flat")
                    service_table.props(f'visible-columns={"Service,UDP,TCP"}')  # Only show these
                    
                    service_table.add_slot('header', r'''
                        <q-tr :props="props">
                            <q-th auto-width />
                            <q-th v-for="col in props.cols" :key="col.name" :props="props"> {{ col.label }} </q-th>
                            <q-th auto-width />
                        </q-tr>
                    ''')
                    
                    async def handle_remove_service(e, zone=zoneName):
                        await removeServiceFromZone(zone, e.args)
    
                    service_table.on('remove-service', handle_remove_service)
                    
                    service_table.add_slot('body', r'''
                    <q-tr :props="props">
                        <!-- expand button -->
                        <q-td auto-width>
                            <q-btn size="sm" color="accent" round dense @click="props.expand = !props.expand" :icon="props.expand ? 'remove' : 'add'" />
                        </q-td>
                        <!-- normal columns -->
                        <q-td v-for="col in props.cols" :key="col.name" :props="props">
                            {{ col.value }}
                        </q-td>
                        <!-- 3-dot menu -->
                        <q-td auto-width>
                            <q-btn flat round dense icon="more_vert" color="accent">
                                <q-menu auto-close>
                                    <q-list style="min-width: 150px">
                                        <q-item clickable
                                            @click="$parent.$emit('remove-service', props.row.Service)">
                                            <q-item-section class="text-negative">
                                                Delete
                                            </q-item-section>
                                        </q-item>
                                    </q-list>
                                </q-menu>
                            </q-btn>
                        </q-td>
                    </q-tr>
                    <!-- expanded description -->
                    <q-tr v-show="props.expand" :props="props">
                        <q-td colspan="100%" style="max-width: 0;">
                            <div class="text-left"
                                 style="word-wrap: break-word; overflow-wrap: break-word; white-space: normal;">
                                {{ props.row.Description }}
                            </div>
                        </q-td>
                    </q-tr>
                    ''')

    pass # end of this... 




@ui.refreshable
async def firewall_table():
    
    start = time.perf_counter()
    
    AppBus = await get_dbus()

    firewallInfo = FirewallInfo()
    
    firewallInfo.Enable = await isActive(AppBus, "firewalld.service")
    firewallInfo.Status = (await getServiceState(AppBus, "firewalld.service")).capitalize()
    
    if firewallInfo.Enable:
        firewallInfo.ActiveZones = await GetZones(AppBus)
        
        for az in firewallInfo.ActiveZones:
            
            zoneInfo = await GetZoneInfo(AppBus, az) 
            
            for s in zoneInfo.Services:
                serviceSettings = await GetServiceSettings2(AppBus, s)          
                if serviceSettings.Includes:
                    for i in serviceSettings.Includes:
                        ser_set = await GetServiceSettings2(AppBus, i)
                        serviceSettings.Ports.extend(ser_set.Ports)
        
                zoneInfo.ServiceSettings[s] = serviceSettings                
            firewallInfo.ZoneInfos[az] = zoneInfo
    await zone_list(firewallInfo)
    
    print(time.perf_counter() - start)
    
    
    
    
    
    





#def daemon_cb(mystr):
#    print(mystr)
#    firewall_table.refresh()

async def firewall_page():
    
    
    #fire = await GetFirewall(dbus.AppBus)
    #fire.on_daemon_changed(daemon_cb)
    start = time.perf_counter()
    with ui.card():
        with ui.row():
            ui.link("Networking", "/networking").classes('text-accent')
            ui.label(">")
            ui.label('firewall')
        print("1 ", time.perf_counter()-start)
        #await firewall_status(False)
        print("2 ",time.perf_counter()-start)
        await firewall_table()
        print("3 ", time.perf_counter()-start)
