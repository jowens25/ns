from nicegui import ui, app, binding
from ns2.networking import *
from ns2.firewalld import *
from dbus_next.signature import Variant
from dbus_next.errors import DBusError
from dbus_next.aio.proxy_object import ProxyInterface
from ns2.dbus import get_dbus

from ns2.firewalld_page import firewall_status




async def network_page():
    AppBus = await get_dbus()

    print("NETWORK PAGE")

    with ui.column().classes("w-full"):
            with ui.card().classes("w-full").props('flat'):
                await firewall_status(True)
            
            interfaces = await GetInterfacesAndAddresses(AppBus)
            
            interface_table = ui.table(
                title="Interfaces",
                rows=interfaces,
                # rows=[{'d':'v'}],
                column_defaults={
                    "align": "left",
                    "headerClasses": "uppercase text-primary",
                },
            ).classes("w-full").props('flat')
            
            interface_table.add_slot(
                "body-cell-name",
                """
                <q-td :props="props">
                    <a :href="'/networking/' + props.row.name" 
                       class="text-accent cursor-pointer hover:underline"
                       >
                        {{ props.value }}
                    </a>
                </q-td>
            """,
            )
            interface_table.add_slot(
                "body-cell-addresses",
                """
                <q-td :props="props" class="font-bold text-sm">
                    {{ props.value }}
                </q-td>
            """,
            )

        #with ui.card():


    

@ui.refreshable
async def interface_card(nm : ProxyInterface, device: ProxyInterface, interface):

    with ui.card().props('flat'):
        with ui.row():
            ui.link("Networking", "/networking").classes('text-accent')
            ui.label(">")
            ui.label(interface.Name)
            ui.label(interface.Active)

            with ui.row().classes("w-full items-center justify-between"):
                ui.label().classes("text-h6").bind_text(interface, "Name")
                ui.label().classes("text-h6").bind_text(interface, "HardwareAddress")
                async def connection_sw_cb(e):
                    action = "enable" if e.sender.value else "disable"
                    with ui.dialog() as dialog, ui.card():
                        ui.label(f"Are you sure you want to {action} this connection?")
                        with ui.row():
                            ui.button(
                                "Cancel", on_click=lambda: dialog.submit("Cancel")
                            ).props("flat color=accent align=left")
                            ui.button(
                                f"{action}", on_click=lambda: dialog.submit(action)
                            ).props("flat color=accent align=left")
                    result = await dialog
                    if result == "enable":
                        await nm.call_activate_connection("/", interface._dev_path, "/")
                    elif result == "disable":
                        await nm.call_deactivate_connection(interface._act_con_path)
                    else:
                        print('canceled')
                    
                    interface_card.refresh()


                ui.switch("Connected").on("click", lambda e: connection_sw_cb(e)).props(
                    "flat color=accent"
                ).bind_value_from(interface, "Active")
        ui.separator()
        
        #ui.spinner(size='lg').bind_visibility_from(interface, "Active", backward=lambda e: (not e))

        with ui.column().classes("flex-1 gap-4"):
            with ui.row().classes("flex-1 gap-16"):
                ui.label("Status").classes("font-bold w-8")
                ui.label().bind_text_from(interface, "Status")
            with ui.row().classes("flex-1 gap-16"):
                ui.label("State").classes("font-bold w-8")
                ui.label().bind_text_from(interface, "StateString")
            with ui.row().classes("flex-1 gap-16"):
                ui.label("Carrier").classes("font-bold w-8")
                ui.label().bind_text_from(interface, "Carrier")
            with ui.row().classes("flex-1 gap-16"):
                ui.label("General").classes("font-bold w-8")
                async def auto_connect_cb(e):
                    return
                    device = GetDevice(dbus.Bus, interface._dev_path)
                    settings = await GetSettings(device)
                    settings["connection"]["autoconnect"] = Variant(
                        "b", e.value
                    )
                    # await connection.call_update2(settings, 0x1, {})
                    # await device.call_reapply(settings, 0, 0)
                ui.checkbox(
                    "Connect automatically", on_change=auto_connect_cb
                ).props("flat color=accent dense").bind_value(
                    interface, "AutoConnect"
                )
                
                
            with ui.row().classes("flex-1 gap-16"):
                ui.label("IPv4").classes("font-bold w-8")
                ui.label().bind_text_from(interface, "Ip4")
                ui.label("Edit").classes(
                    "text-accent cursor-pointer hover:underline"
                ).on("click", lambda: edit_ip_connection('ipv4', device))
                
                
            with ui.row().classes("flex-1 gap-16"):
                ui.label("IPv6").classes("font-bold w-8")
                ui.label().bind_text_from(interface, "Ip6")
                ui.label("Edit").classes(
                    "text-accent cursor-pointer hover:underline"
                ).on("click", lambda: edit_ip_connection('ipv6', device))



async def interface_page(interface_name: str):
    AppBus = await get_dbus()

    nm = GetNetworkManager(AppBus)

    dev_path = await nm.call_get_device_by_ip_iface(interface_name)

    device = GetDevice(AppBus, dev_path)

    interface = await GetInterfaceData(AppBus, nm, interface_name)

    await interface_card(nm, device, interface)
    
    async def state_changed_cb(u1, u2, u3):
        
        print(u1, u2, u3)
        # Re-fetch the interface data to get the new state
        updated_interface = await GetInterfaceData(AppBus, nm, interface_name)
        
        # Update the existing interface object's properties
        # This will trigger the UI bindings to update automatically
        interface.Status = updated_interface.Status
        interface.StateString = updated_interface.StateString
        interface.StateNumber = updated_interface.StateNumber
        interface.Carrier = updated_interface.Carrier
        interface.Active = updated_interface.Active
        interface.Ip4 = updated_interface.Ip4
        interface.Ip6 = updated_interface.Ip6
        # Add any other properties that might change
    
    device.on_state_changed(state_changed_cb)




async def edit_ip_connection(version: str, device: ProxyInterface):
    AppBus = await get_dbus()

    settings = await GetSettings(AppBus, device)

    ip = GetIp(version, settings)

    connection = await GetConnectionFromDevice(AppBus, device)

    def add_ip_address(a: str = None, p: str = None, g: str = None):
        ip.AddressData.append(IpAddress(a, p))
        ip_address_list.refresh()

    def remove_ip_address(addr):
        ip.AddressData.remove(addr)
        ip_address_list.refresh()

    def add_dns_server(server: str = None):
        ip.DnsData.append(DnsServer(server))
        dns_server_list.refresh()

    def remove_dns_server(dns):
        ip.DnsData.remove(dns)
        dns_server_list.refresh()

    def add_dns_search(search: str = None):
        ip.DnsSearch.append(DnsServer(search))
        dns_search_list.refresh()

    def remove_dns_search(search):
        ip.DnsSearch.remove(search)
        dns_search_list.refresh()

    def add_route(
        Address: str = None, Prefix: str = None, NextHop: str = None, Metric: str = None
    ):
        ip.RouteData.append(IpRoute(Address, Prefix, NextHop, Metric))
        route_list.refresh()

    def remove_route(route):
        ip.RouteData.remove(route)
        route_list.refresh()

    @ui.refreshable
    async def ip_address_list():
        for addr in ip.AddressData:
            with ui.row():
                ui.input(label="Address").props("dense").classes("flex-1").bind_value(
                    addr, "Address"
                )
                ui.input(label="Prefix").props("dense").classes(
                    "flex-1"
                ).bind_value(addr, "Prefix")
                ui.input(label="Gateway").props("dense").classes("flex-1").bind_value(
                    ip, "Gateway"
                )
                ui.button(
                    icon="delete", on_click=lambda a=addr: remove_ip_address(a)
                ).props("flat color=accent").props("dense")

    @ui.refreshable
    async def dns_server_list():
        for dns in ip.DnsData:
            with ui.row():
                ui.input(label="Server").props("dense").classes("flex-1").bind_value(
                    dns, "Server"
                )
                ui.button(
                    icon="delete", on_click=lambda d=dns: remove_dns_server(d)
                ).props("flat color=accent").props("dense")

    @ui.refreshable
    async def dns_search_list():
        for search in ip.DnsSearch:
            with ui.row():
                ui.input(label="Server").props("dense").classes("flex-1").bind_value(
                    search, "Server"
                )
                ui.button(
                    icon="delete", on_click=lambda d=search: remove_dns_search(d)
                ).props("flat color=accent").props("dense")

    @ui.refreshable
    async def route_list():
        for route in ip.RouteData:
            with ui.row():
                ui.input(label="Server").props("dense").classes("flex-1").bind_value(
                    route, "Dest"
                )
                ui.input(label="Prefix or netmask").props("dense").classes(
                    "flex-1"
                ).bind_value(route, "Prefix")
                ui.input(label="Next Hop").props("dense").classes("flex-1").bind_value(
                    route, "NextHop"
                )
                ui.input(label="Metric").props("dense").classes("flex-1").bind_value(
                    route, "Metric"
                )

                ui.button(
                    icon="delete", on_click=lambda d=route: remove_route(d)
                ).props("flat color=accent").props("dense")

    ###
    with ui.dialog() as dialog:
        with ui.card().classes("w-full self-start max-h-[90vh] overflow-y-auto"):
            ui.label(f"{version.capitalize()} settings").classes("text-h5")
            with ui.column().classes("w-full"):

                ### ADDRESSES
                with ui.row().classes("w-full justify-between"):
                    ui.label("Addresses")
                    with ui.row():

                        def on_method_change(e):
                            # SetIp4Method(settings, e.value)
                            return

                        ui.select(
                            options=["disabled", "auto", "manual"],
                            on_change=on_method_change,
                        ).props("dense").classes("w-24").bind_value(ip, "Method")

                        ip_address_button = ui.button(
                            icon="add", on_click=add_ip_address
                        ).props("flat color=accent dense")

                with ui.column().classes("items-center justify-between gap-4 w-full"):
                    await ip_address_list()
                    print()
                ###

                ### DNS SERVER
                ui.separator()
                with ui.row().classes("w-full justify-between"):
                    ui.label("DNS Servers")
                    with ui.row():

                        dns_server_switch = (
                            ui.switch("Automatic")
                            .props("flat color=accent dense")
                            .classes("w-24")
                            .bind_value(
                                ip,
                                "IgnoreAutoDns",
                                forward=lambda x: not x,
                                backward=lambda x: not x,
                            )
                        )
                        dns_server_button = ui.button(
                            icon="add",
                            on_click=add_dns_server,
                        ).props("flat color=accent dense")
                with ui.column().classes("items-center justify-between gap-4 w-full"):
                    await dns_server_list()
                ###

                ### DNS SEARCH
                ui.separator()
                with ui.row().classes("w-full justify-between"):
                    ui.label("DNS Searches")
                    with ui.row():
                        dns_search_button = (
                            ui.button(
                                icon="add",
                                on_click=add_dns_search,
                            )
                            .props("flat color=accent")
                            .props("dense")
                        )
                with ui.column().classes("items-center justify-between gap-4 w-full"):
                    await dns_search_list()
                ###

                ### ROUTES
                ui.separator()
                with ui.row().classes("w-full justify-between"):
                    ui.label("Routes")
                    with ui.row():
                        route_switch = (
                            ui.switch("Automatic")
                            .props("flat color=accent")
                            .props("dense")
                            .classes("w-24")
                            .bind_value(
                                ip,
                                "IgnoreAutoRoutes",
                                forward=lambda x: not x,
                                backward=lambda x: not x,
                            )
                        )
                        route_button = (
                            ui.button(icon="add", on_click=add_route)
                            .props("flat color=accent")
                            .props("dense")
                        )
                with ui.column().classes("items-center justify-between gap-4 w-full"):
                    await route_list()
                ###

                with ui.row().classes("items-center justify-between gap-4 w-full"):

                    async def on_save_cb():
                        try:

                            _settings = SetIp(ip, version, settings)

                            _settings = ApplyModes(version, _settings)

                            await connection.call_update2(_settings, 0x1, {})

                            await device.call_reapply(_settings, 0, 0)

                            dialog.close()

                        except DBusError as e:
                            ui.notify(e, type="negative")
                            # dialog.close()

                        except Exception as e:
                            print(e)
                            ui.notify("Please correct the errors", type="negative")

                    def on_cancel_cb():
                        dialog.close()

                    save_button = ui.button("save", on_click=on_save_cb).props(
                        "flat color=accent align=left"
                    )
                    cancel_button = ui.button("cancel", on_click=on_cancel_cb).props(
                        "flat color=accent align=left"
                    )
    await dialog
