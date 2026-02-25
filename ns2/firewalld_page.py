from nicegui import ui, app, binding
from ns2.networking import *
from ns2.firewalld import *
from dbus_next.signature import Variant
from dbus_next.errors import DBusError
from dbus_next.aio.proxy_object import ProxyInterface
from ns2.dbus import get_dbus

from ns2.systemd import *
from ns2.common import formatStringToList

@ui.refreshable
async def firewall_status(on_network_page: bool):
    AppBus = await get_dbus()

    print("FIREWALL STATUS")
    firewallInfo = FirewallInfo()
    firewallInfo.Enable = await isActive(AppBus, 'firewalld.service')
    firewallInfo.Status = (await getServiceState(AppBus, "firewalld.service")).capitalize()
    numActiveZones = 0
    if firewallInfo.Enable:
        numActiveZones = len(await GetActiveZones(AppBus))
        
    
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
                    await zone_list.refresh()

                ui.switch(f"Status: {firewallInfo.Status}").on('click', lambda e: fire_switch_cb(e)
                        ).props("flat color=accent align=left dense").bind_value(firewallInfo, "Enable").bind_text

            if on_network_page:
                ui.button("Edit rules and zones", on_click=lambda e: ui.navigate.to('/networking/firewall')).props("flat color=accent align=left dense")

            else:
                
                async def open_dialog():
                    zoneDialog = await addZoneDialog()
                    print("dialog created then opened")
                    zoneDialog.open()
                ui.button("add new zone", on_click=open_dialog).props("color=accent align=left")
        

 
    
def InterfaceText(interfaces):
    print(interfaces)
    if len(interfaces) == 1:
        l1 = ui.label("Interface:").classes("font-bold")
    else:
        l1= ui.label("Interfaces:").classes("font-bold")
    l2 = ui.label(formatListToString(interfaces))
    return (l1, l2)

def AllowedAddressText(sources):
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
    return f'removed {serviceName} from {zoneName}'

async def addServiceToZone(zoneName: str, serviceName: str):
    AppBus = await get_dbus()
    try: 
        print(f'add {serviceName} to {zoneName}')
        zone = await GetFirewalldZone(AppBus)

        res = await zone.call_add_service(zoneName, serviceName, 0)
        print("res1: ", res)

        conf = await GetFirewalldConfig(AppBus)
        p = await conf.call_get_zone_by_name(zoneName)

        print(p)

        configZone = await GetFirewalldConfigZone(AppBus, p)
        res = await configZone.call_add_service(serviceName)
        print(res)

        #await get_firewall_info()
        
    except DBusError as e:
        return e
        
    return f'added {serviceName} to {zoneName}'


async def serviceSelectionTable():
    AppBus = await get_dbus()

    services = formatServicesInRows(await getServicesInfo(AppBus))

    with ui.scroll_area().classes("w-full"):
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
        services_table.add_slot('header', r'''
            <q-tr :props="props">
                <q-th auto-width />
                <q-th auto-width />
                <q-th v-for="col in props.cols" :key="col.name" :props="props"> {{ col.label }} </q-th>
            </q-tr>
        ''')

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
        
    serviceFilter = ui.input('Search for services').bind_value(services_table, "filter")
    return services_table


            
def validate_group(group: list):
    return [x.validate() for x in group]

async def addZoneDialog():

    AppBus = await get_dbus()

    with ui.dialog() as dialog:
        with ui.card().props('flat'):
            ui.label("Add zone").classes("text-h5")
            
            with ui.row() as trust:
                ui.label("Trust level")
                zone_description = ui.label()
                
            with ui.column():
                zoneSelection = ui.radio(await GetSelectableZones(AppBus)).props("dense")
                zone_description.bind_text_from(zoneSelection, 'value', backward=lambda e: zoneDescriptionMap[e])
                
            
            ui.label("Interfaces").classes("text-h6")

            with ui.row():
                interfaces = {}
                selected_interfaces = []
                for i in await GetAvailableInterfaces(AppBus):
                    #interfaces[i] = False
                    ui.checkbox(i).props("flat color=accent align=left dense").bind_value(interfaces, i)

            #selectedServices = ui.input_chips('Allowed services', new_value_mode='add-unique', clearable=True).props('disable-input')
            #serviceTable = await serviceSelectionTable()
            
            #services = [serviceDict['Service'] for serviceDict in serviceTable.selected]

            
            with ui.row():
                addresses = []
                ui.label("Allowed Addresses").classes("text-h6")
                addressSelection = ui.radio(["Entire subnet", "Range"], value="Entire subnet").props("dense, inline")
                ui.label("IP address with routing prefix.\
                         Separate multiple values with a comma. \
                        Example: 192.0.2.0/24, 2001:db8::/32").bind_visibility_from(addressSelection, 'value', backward=lambda e: e == "Range").props("dense").classes("w-full")
                addr = ui.input("allowed addresses").bind_visibility_from(addressSelection, 'value', backward=lambda e: e == "Range").props("dense").classes("w-full")


            async def on_save_cb():
                addresses = []
                for c,v in interfaces.items():
                    if v:
                        selected_interfaces.append(c)
                if addressSelection == "Range":
                    addresses = formatStringToList(addr.value)
    
                print("add zone....")
                rsp = await AddZone(AppBus, 
                           zoneSelection.value,
                           selected_interfaces,
                           addresses)
                
                dialog.close()
                zone_list.refresh()
                
            with ui.row():
                ui.button('Add zone', on_click=on_save_cb).props("color=accent align=left")
                ui.button('Cancel', on_click=dialog.close).props("flat color=accent align=left")

    return dialog

async def addServiceDialog(zoneName):
    with ui.dialog() as dialog:
        with ui.card().props('flat').classes("w-full"):
            ui.label(f"Add services to {zoneName}").classes("text-h5")
            
            #selectedServices = ui.input_chips('Allowed services', new_value_mode='add-unique', clearable=True).props('disable-input')
            tab = await serviceSelectionTable()


            async def on_add_cb():                
                print(tab.selected)
                for service in tab.selected:
                    serviceName = service['Service']
                    rsp = await addServiceToZone(zoneName, serviceName)
                    await zoneServicesTable.refresh()
                dialog.close()
                
                ui.notify(rsp)
            
            with ui.row():
                ui.button('Add', on_click=on_add_cb).props("color=accent align=left")
                ui.button('Cancel', on_click=dialog.close).props("flat color=accent align=left")

    return dialog

@ui.refreshable
async def zoneServicesTable(zonePath: str):
    AppBus = await get_dbus()
    #zonePath = 
    
    zoneInfo = MakeZoneInfo(await GetSettings2(AppBus, zonePath)) 
    
    services = formatServicesInRows(await getAllServices(zoneInfo))
                     
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
    
    async def handle_remove_service(e, zone=zoneInfo.Name):
        rsp = await removeServiceFromZone(zone, e.args)
        await zoneServicesTable.refresh()
        ui.notify(rsp)

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
async def zone_list():
    #firewallInfo = await get_firewall_info()
    AppBus = await get_dbus()
    #await GetAllZones(AppBus)
    with ui.column():
        if await isActive(AppBus, "firewalld.service"):
            for zoneName in (await GetActiveZones(AppBus)):
                
                zonePath = await GetZoneByName(AppBus, zoneName)
                settings = await GetSettings2(AppBus, zonePath)
                
                print(settings)
                
                settings = await GetZoneSettings2(AppBus, zoneName)
                #print("other ", other_settings)
                
                interfaces = settings.get('interfaces', Variant('as', [])).value
                sources = settings.get('sources', Variant('as', [])).value
                
                with ui.card().classes("w-full").props('flat').classes("bg-secondary"):
                    with ui.column():
                        with ui.row().classes("w-full items-baseline justify-between"):
                            with ui.row().classes("items-baseline"):
                                ui.label(f'{zoneName.capitalize()} zone')
                                InterfaceText(interfaces)

                            with ui.row():
                                AllowedAddressText(sources)

                            with ui.row():
                                async def open_service_dialog(z=zoneName):
                                    addDialog = await addServiceDialog(z)
                                    addDialog.open()
                                ui.button("add services", on_click=open_service_dialog).props("color=accent align=left")

                                async def delete_zone_cb(e, z=zoneName):
                                    with ui.dialog() as dialog, ui.card():
                                        ui.label(f'Are you sure you want to delete the {z} zone?')
                                        with ui.row():
                                            ui.button('Cancel', on_click=lambda: dialog.submit("Cancel")).props("flat color=accent align=left")
                                            ui.button('Delete', on_click=lambda: dialog.submit("Delete")).props("flat color=accent align=left")
                                    result = await dialog
                                    if result == "Delete":
                                        await RemoveZone(AppBus, z)
                                    await firewall_status.refresh()
                                    await zone_list.refresh()
                                with ui.dropdown_button(icon="more_vert").props("flat color=accent align=left"):
                                    ui.item('delete', on_click=delete_zone_cb)


                    await zoneServicesTable(zonePath)
                    
                    




async def getAllServices(zoneInfo: ZoneInfo):
    services = {}
    AppBus = await get_dbus()
    for s in zoneInfo.Services:
        serviceSettings = await GetServiceSettings2(AppBus, s)          
        if serviceSettings.Includes:
            for i in serviceSettings.Includes:
                ser_set = await GetServiceSettings2(AppBus, i)
                serviceSettings.Ports.extend(ser_set.Ports)
        services[s] = serviceSettings
    return services
  

async def firewall_page():
    with ui.card():
        with ui.row():
            ui.link("Networking", "/networking").classes('text-accent')
            ui.label(">")
            ui.label('firewall')
        await firewall_status(False)
        await zone_list()
