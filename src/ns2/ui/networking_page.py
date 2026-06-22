from nicegui import ui, app
from ns2.lib.bridge import CanOpenDialog
from ns2.lib.networking import (
    GetInterfacesAndAddresses,
    InterfaceData,
    GetNmProp,
    GetInterfaceData,
    GetSettings,
    IpAddress,
    DnsServer,
    IpRoute,
    GetIp,
    SetIp,
    ApplyModes,
    ConnectionUpdate2,
    DeviceReapply,
)

from dbus_next.signature import Variant
from dbus_next.errors import DBusError

from ns2.ui.control_panel import controlPanel
from ns2.utils import log

from ns2.ui.firewalld_page import firewall_card


@ui.page("/network")
async def network_page():

    await controlPanel()

    with ui.column().classes("w-full"):

        interfaces = await GetInterfacesAndAddresses()

        for i in interfaces:

            await interface_card(await GetInterfaceData(i["name"]))

        await firewall_card()


@ui.refreshable
async def interface_card(interface: InterfaceData):

    with ui.card().props("flat"):
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("Network").classes("text-h5")

            ui.label().classes("text-h5").bind_text(interface, "Name").props(
                "font-bold"
            )
            ui.label().classes("text-h6").bind_text(interface, "HardwareAddress")

        ui.separator()

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
                ui.label("IPv4").classes("font-bold w-8")
                ui.label().bind_text_from(interface, "Ip4Gateway")
                ui.label().bind_text_from(interface, "Ip4")
                ui.label("Edit").classes(
                    "text-accent cursor-pointer hover:underline"
                ).on("click", lambda: edit_ip_connection("ipv4", interface))

            with ui.row().classes("flex-1 gap-16"):
                ui.label("IPv6").classes("font-bold w-8")
                ui.label().bind_text_from(interface, "Ip6Gateway")

                ui.label().bind_text_from(interface, "Ip6")
                ui.label("Edit").classes(
                    "text-accent cursor-pointer hover:underline"
                ).on("click", lambda: edit_ip_connection("ipv6", interface))


async def edit_ip_connection(version: str, id: InterfaceData):

    u = app.storage.general.get("activeUser", "error")
    rsp = await CanOpenDialog(u)
    if rsp.error_name is not None:
        ui.notify(rsp.body[0])
        return
    CanOpen = rsp.body[0]
    if not CanOpen:
        ui.notify("must be an admin to edit network settings", type="warning")
        return
    connection_path = await GetNmProp(
        id.act_con_path, "Connection.Active", "Connection"
    )

    settings = await GetSettings(connection_path)
    if version == "ipv6":
        settings[version]["gateway"] = Variant(
            "s", await GetNmProp(id.ip6_config_path, "IP6Config", "Gateway")
        )
    settings[version]["gateway"] = Variant(
        "s", await GetNmProp(id.ip4_config_path, "IP4Config", "Gateway")
    )

    ip = GetIp(version, settings)

    # connection = await GetConnectionFromDevice(AppBus, device)

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
                ui.input(label="Prefix").props("dense").classes("flex-1").bind_value(
                    addr, "Prefix"
                )
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

                        ui.button(icon="add", on_click=add_ip_address).props(
                            "flat color=accent dense"
                        )

                with ui.column().classes("items-center justify-between gap-4 w-full"):
                    await ip_address_list()
                    log.info("ip address list")
                ###

                ### DNS SERVER
                ui.separator()
                with ui.row().classes("w-full justify-between"):
                    ui.label("DNS Servers")
                    with ui.row():

                        ui.switch("Automatic").props("flat color=accent dense").classes(
                            "w-24"
                        ).bind_value(
                            ip,
                            "IgnoreAutoDns",
                            forward=lambda x: not x,
                            backward=lambda x: not x,
                        )

                        ui.button(
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

                        ui.button(
                            icon="add",
                            on_click=add_dns_search,
                        ).props("flat color=accent dense")

                with ui.column().classes("items-center justify-between gap-4 w-full"):
                    await dns_search_list()
                ###

                ### ROUTES
                ui.separator()
                with ui.row().classes("w-full justify-between"):
                    ui.label("Routes")
                    with ui.row():

                        ui.switch("Automatic").props("flat color=accent dense").classes(
                            "w-24"
                        ).bind_value(
                            ip,
                            "IgnoreAutoRoutes",
                            forward=lambda x: not x,
                            backward=lambda x: not x,
                        )

                        ui.button(icon="add", on_click=add_route).props(
                            "flat color=accent dense"
                        )

                with ui.column().classes("items-center justify-between gap-4 w-full"):
                    await route_list()
                ###

                with ui.row().classes("items-center justify-between gap-4 w-full"):

                    async def on_save_cb():
                        try:

                            _settings = SetIp(ip, version, settings)

                            _settings = ApplyModes(version, _settings)

                            rsp = await ConnectionUpdate2(
                                connection_path, _settings, 0x1, {}
                            )

                            if rsp.error_name is not None:
                                ui.notify(f"{rsp.body[0]}", type="warning")
                            else:
                                ui.notify("Updated network settings", type="positive")

                            rsp = await DeviceReapply(id.dev_path, _settings, 0, 0)

                            dialog.close()

                        except DBusError as e:
                            ui.notify(e, type="negative")
                            # dialog.close()

                        # except Exception as e:
                        #    log.info(e)
                        #    ui.notify("Please correct the errors", type="negative")

                    def on_cancel_cb():
                        dialog.close()

                    ui.button("save", on_click=on_save_cb).props(
                        "flat color=accent align=left"
                    )
                    ui.button("cancel", on_click=on_cancel_cb).props(
                        "flat color=accent align=left"
                    )
    await dialog
