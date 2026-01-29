from nicegui import ui, app, binding
from ns.lib.networking import *
from ns.lib.firewalld import *
from dbus_next.signature import Variant
from dbus_next.errors import DBusError
from dbus_next.aio.proxy_object import ProxyInterface
from ns.dbus import dbus

from ns.lib.systemd import *

async def interface_list(checks: dict):
    for i in await GetInterfaces(dbus.AppBus):
        checks[i] = False
        ui.checkbox(i).props("flat color=accent align=left").bind_value(checks, i)

async def service_list(services: dict):
    for s in await getServices(dbus.AppBus):
        with ui.row():
            ui.checkbox(s).props("flat color=accent align=left").bind_value(services, s)

            with ui.column():
                ui.label().bind_text_from(s, "UDP")
                ui.label().bind_text_from(s, "TCP")


@ui.refreshable
async def firewall_status(on_network_page: bool):

    firewall = Firewall()
    firewall.Enable = await isActive(dbus.AppBus, 'firewalld.service')
    firewall.Status = (await getServiceState(dbus.AppBus, "firewalld.service")).capitalize()
    numActiveZones = 0
    if firewall.Enable:
        zone = await GetFirewalldZone(dbus.AppBus)
        numActiveZones = len(await zone.call_get_active_zones())
        
    
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
                    active = await isActive(dbus.AppBus, "firewalld.service")
                    if result == "enable" and not active:
                        await systemd_start(dbus.AppBus, "firewalld.service")
                    if result == "disable" and active:
                        await systemd_stop(dbus.AppBus, "firewalld.service")
                    await firewall_status.refresh()

                ui.switch(f"Status: {firewall.Status}").on('click', lambda e: fire_switch_cb(e)
                        ).props("flat color=accent align=left dense").bind_value(firewall, "Enable").bind_text

            if on_network_page:
                ui.button("Edit rules and zones", on_click=lambda e: ui.navigate.to('/networking/firewall')).props("flat color=accent align=left dense")

            else:
                zoneDialog = await addZoneDialog()
                ui.button("add new zone", on_click=zoneDialog.open).props("color=accent align=left")
        

 


    
    
def InterfaceText(zoneSettings :ZoneSetting):
    interfaces = zoneSettings.Interfaces
    if len(interfaces) == 1:
        l1 = ui.label("Interface:").classes("font-bold")
    else:
        l1= ui.label("Interfaces:").classes("font-bold")
    l2 = ui.label(formatListToString(interfaces))
    return (l1, l2)

def AllowedAddressText(zoneSettings :ZoneSetting):
    sources = zoneSettings.Sources
    l1 = ui.label("Allowed Addresses:").classes("font-bold")
    if len(sources) == 0:
        l2 = ui.label("Entire subnet")
    else:
        l2 = ui.label(formatListToString(sources))
    return (l1, l2)




async def removeServiceFromZone(zoneName: str, serviceName:str):
    
    print(f'remove {serviceName} from {zoneName}')
    zone = await GetFirewalldZone(dbus.AppBus)
    
    res = await zone.call_remove_service(zoneName, serviceName)
    print("res1: ", res)
    conf = await GetFirewalldConfig(dbus.AppBus)
    
    p = await conf.call_get_zone_by_name(zoneName)
    
    print(p)
    
    configZone = await GetFirewalldConfigZone(dbus.AppBus, p)
    res = await configZone.call_remove_service(serviceName)
    print(res)
    return



async def addZoneDialog():
    with ui.dialog() as dialog:
        with ui.card().props('flat'):
            ui.label("Add zone").classes("text-h5")
            ui.label("Interfaces").classes("text-h6")

            with ui.row():
                checks = {}
                await interface_list(checks)

            #selectedServices = ui.input_chips('Allowed services', new_value_mode='add-unique', clearable=True).props('disable-input')
            with ui.scroll_area():
                services = formatServicesInRows(await getServices(dbus.AppBus))
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
                for c,v in checks.items():
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
        for zoneName, zoneSetting in firewall.ZoneSettings.items():
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
                    
                    services = formatServicesInRows(firewall.ZoneSettings[zoneName].ServiceSettings)
                    
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
    
    firewall = Firewall()
    #fire = await GetFirewall(dbus.AppBus)
    firewall.Enable = await isActive(dbus.AppBus, "firewalld.service")
    firewall.Status = (await getServiceState(dbus.AppBus, "firewalld.service")).capitalize()
    
    if firewall.Enable:
        fire = await GetFirewalld(dbus.AppBus)
        zone = await GetFirewalldZone(dbus.AppBus)
        firewall.ActiveZones = await zone.call_get_active_zones()
        
        for az in firewall.ActiveZones:
            
            zs = ZoneSetting()
            
            zoneSettings = await zone.call_get_zone_settings2(az)
            
            zs.Description = zoneSettings.get('description', Variant('s', 'description not available')).value
            zs.Interfaces = zoneSettings.get('interfaces', Variant('as', [])).value
            zs.Services = zoneSettings.get('services', Variant('as', [])).value
            zs.Short = zoneSettings.get('short', Variant('s', 'short not available')).value
            zs.Sources = zoneSettings.get('sources', Variant('as', [])).value
            
            for s in zs.Services:
                serSet = ServiceSetting()
                serviceSettings = await fire.call_get_service_settings2(s)
                                
                includes = serviceSettings.get('includes', False)
                if includes:
                    for i in includes.value:
                        ser_set = await fire.call_get_service_settings2(i)
                        serSet.Ports.extend(ser_set.get('ports', Variant('a(ss)', [['port not available', 'protocol not available']])).value)
        
                                    
                serSet.Name = serviceSettings.get('short', Variant('s', 'name not available')).value
                serSet.Ports.extend(serviceSettings.get('ports', Variant('a(ss)', [['port not available', 'protocol not available']])).value)
                serSet.Description = serviceSettings.get('description', Variant('s', 'Description not available')).value
                zs.ServiceSettings[s] = serSet
                #pprint(service_settings)
                
            firewall.ZoneSettings[az] = zs

    await zone_list(firewall)
    
    
    
    
    
    





#def daemon_cb(mystr):
#    print(mystr)
#    firewall_table.refresh()

async def firewall_page():
    
    
    #fire = await GetFirewall(dbus.AppBus)
    #fire.on_daemon_changed(daemon_cb)

    with ui.card():
        with ui.row():
            ui.link("Networking", "/networking").classes('text-accent')
            ui.label(">")
            ui.label('firewall')
        await firewall_status(False)
        await firewall_table()