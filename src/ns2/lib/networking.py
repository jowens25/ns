from dataclasses import field
from typing import Optional
from nicegui import binding

from dbus_next.signature import Variant
from dbus_next import Message
from ns2.common import formatListToString

from ns2.lib.bridge import BridgeCall
from ns2.utils import log

# ====================================================================
# data classes
# ====================================================================


class ConnectionDetails:
    Id: Optional[str] = ""
    Permissions: Optional[list[str]] = None
    Timestamp: Optional[int] = 0
    Type: Optional[str] = ""
    Uuid: Optional[str] = ""


@binding.bindable_dataclass
class IpAddress:
    Address: Optional[str] = None
    Prefix: Optional[int] = None


@binding.bindable_dataclass
class DnsServer:
    Server: Optional[str] = ""


@binding.bindable_dataclass
class IpRoute:
    Dest: Optional[str] = None
    Prefix: Optional[int] = None
    NextHop: Optional[str] = None
    Metric: Optional[int] = None


@binding.bindable_dataclass
class Ipv4v6:
    AddressData: Optional[list[IpAddress]] = field(default_factory=list)  # used
    # Addresses:        Optional[list[list[int]]] = field(default_factory=list) # not used
    # Dns:              Optional[list[list[int]]] = field(default_factory=list) # not used
    DnsData: Optional[list[DnsServer]] = field(default_factory=list)  # used
    DnsSearch: Optional[list[DnsServer]] = field(default_factory=list)  # used
    Gateway: Optional[str] = ""  # used
    IgnoreAutoDns: Optional[bool] = False  # used
    IgnoreAutoRoutes: Optional[bool] = False  # used
    Method: Optional[str] = ""  # used
    RouteData: Optional[list[IpRoute]] = field(default_factory=list)  # used
    # Routes:           Optional[list[list[int]]] = field(default_factory=list) # not used


@binding.bindable_dataclass
class Settings:
    Connection: Optional[ConnectionDetails] = None
    Ipv4: Optional[Ipv4v6] = None
    Ipv6: Optional[Ipv4v6] = None
    Proxy: Optional[str] = ""


@binding.bindable_dataclass
class Device:
    Path: Optional[str] = ""
    ActiveConnectionPath: Optional[str] = ""
    HardwareAddress: Optional[str] = ""
    Flags: Optional[int] = None
    Carrier: Optional[str] = ""
    State: Optional[int] = True
    DeviceState: Optional[str] = ""
    Ip4ConfigPath: Optional[str] = ""
    Ip6ConfigPath: Optional[str] = ""


@binding.bindable_dataclass
class InterfaceData:
    Name: Optional[str] = ""
    HardwareAddress: Optional[str] = ""
    StateString: Optional[str] = ""
    StateNumber: Optional[int] = 0
    Active: Optional[bool] = False
    Status: Optional[str] = ""
    Carrier: Optional[str] = ""
    Ip4: Optional[str] = ""
    Ip6: Optional[str] = ""
    ip4_config_path: Optional[str] = ""
    ip6_config_path: Optional[str] = ""
    AutoConnect: Optional[bool] = False
    dev_path: Optional[str] = ""
    act_con_path: Optional[str] = ""


# ====================================================================
# Proxies
# ====================================================================

INTERFACE = "org.freedesktop.NetworkManager"


async def GetDevices():
    rsp = await BridgeCall(
        destination="org.freedesktop.NetworkManager",
        path="/org/freedesktop/NetworkManager",
        interface="org.freedesktop.NetworkManager",
        member="GetDevices",
        signature="",
        body=[],
    )
    return rsp.body[0]


async def ConnectionUpdate2(
    settings_path: str, settings: dict, flags: int, args: dict
) -> Message:
    return await BridgeCall(
        destination="org.freedesktop.NetworkManager",
        path=settings_path,
        interface="org.freedesktop.NetworkManager.Settings.Connection",
        member="Update2",
        signature="a{sa{sv}}ua{sv}",
        body=[settings, flags, args],
    )


async def DeviceReapply(
    device_path: str, connection: dict, flags: int, args: int
) -> Message:
    return await BridgeCall(
        destination="org.freedesktop.NetworkManager",
        path=device_path,
        interface="org.freedesktop.NetworkManager.Device",
        member="Reapply",
        signature="a{sa{sv}}tu",
        body=[connection, flags, args],
    )


async def GetAppliedConnection(device_path: str, flags: int):
    rsp = await BridgeCall(
        destination="org.freedesktop.NetworkManager",
        path=device_path,
        interface="org.freedesktop.NetworkManager.Device",
        member="GetAppliedConnection",
        signature="u",
        body=[flags],
    )
    return rsp.body[0]


async def set_refresh_rate(device_path: str, rate_ms: int):
    """Set the refresh rate for statistics (in milliseconds)."""

    rsp = await BridgeCall(
        destination="org.freedesktop.NetworkManager",
        path=device_path,
        interface="org.freedesktop.DBus.Properties",
        member="Set",
        signature="ssv",
        body=[
            "org.freedesktop.NetworkManager.Device.Statistics",
            "RefreshRateMs",
            Variant("u", rate_ms),  # 'u' is unsigned int
        ],
    )

    return rsp.body[0]


async def get_device_statistics(device_path: str):

    rsp = await BridgeCall(
        destination="org.freedesktop.NetworkManager",
        path=device_path,  # e.g., '/org/freedesktop/NetworkManager/Devices/1'
        interface="org.freedesktop.DBus.Properties",
        member="GetAll",
        signature="s",
        body=["org.freedesktop.NetworkManager.Device.Statistics"],
    )

    props = rsp
    return {
        "refresh_rate_ms": props.get("RefreshRateMs", 0),
        "tx_bytes": props.get("TxBytes", 0),
        "rx_bytes": props.get("RxBytes", 0),
    }


async def get_device_properties(device_path: str):
    rsp = await BridgeCall(
        destination="org.freedesktop.NetworkManager",
        path=device_path,  # e.g., '/org/freedesktop/NetworkManager/Devices/1'
        interface="org.freedesktop.DBus.Properties",
        member="GetAll",
        signature="s",
        body=["org.freedesktop.NetworkManager.Device"],
    )
    return rsp.body[0]


async def GetDeviceProperty(device_path: str, property: str):
    rsp = await BridgeCall(
        destination="org.freedesktop.NetworkManager",
        path=device_path,  # e.g., '/org/freedesktop/NetworkManager/Devices/1'
        interface="org.freedesktop.DBus.Properties",
        member="Get",
        signature="ss",
        body=["org.freedesktop.NetworkManager.Device", property],
    )
    return rsp.body[0]


async def GetNmProp(
    objectPath: str,
    interface_suffix: str,
    property: str,
):

    root = "org.freedesktop.NetworkManager"

    interface = root
    if interface_suffix is not None:
        interface = ".".join([root, interface_suffix])

    return await GetProperty(root, objectPath, interface, property)


async def GetProperty(
    destination: str,
    objectPath: str,
    interface: str,
    property: str,
):
    rsp = await BridgeCall(
        destination=destination,
        path=objectPath,
        interface="org.freedesktop.DBus.Properties",
        member="Get",
        signature="ss",
        body=[interface, property],
    )

    if type(rsp.body[0]) is Variant:
        return rsp.body[0].value
    else:
        return rsp.body[0]


async def GetSettings(connection_path: str):
    rsp = await BridgeCall(
        destination="org.freedesktop.NetworkManager",
        path=connection_path,
        interface="org.freedesktop.NetworkManager.Settings.Connection",
        member="GetSettings",
        signature="",
        body=[],
    )
    return rsp.body[0]


async def GetDeviceByIpIface(iface: str):
    rsp = await BridgeCall(
        destination="org.freedesktop.NetworkManager",
        path="/org/freedesktop/NetworkManager",
        interface="org.freedesktop.NetworkManager",
        member="GetDeviceByIpIface",
        signature="s",
        body=[iface],
    )
    return rsp.body[0]


# ====================================================================
# Getters and Setters
# ====================================================================


async def GetInterfaceData(iface: str) -> InterfaceData:
    i = InterfaceData()
    i.dev_path = await GetDeviceByIpIface(iface)
    # dev = await GetDevice(bus, i.dev_path)
    i.Name = iface
    i.HardwareAddress = await GetNmProp(i.dev_path, "Device", "HwAddress")
    i.StateNumber = await GetNmProp(i.dev_path, "Device", "State")
    i.StateString = processDeviceState(i.StateNumber)
    i.Active = True if i.StateNumber == 100 else False
    i.Carrier = processInterfaceFlags(
        await GetNmProp(i.dev_path, "Device", "InterfaceFlags")
    )

    i.ip4_config_path = await GetNmProp(i.dev_path, "Device", "Ip4Config")
    i.ip6_config_path = await GetNmProp(i.dev_path, "Device", "Ip6Config")
    i.act_con_path = await GetNmProp(i.dev_path, "Device", "ActiveConnection")

    if len(i.ip4_config_path) > 1:

        ip4AddressData = await GetNmProp(i.ip4_config_path, "IP4Config", "AddressData")

        log.info(ip4AddressData)
        log.info(ip4AddressData)
        ip6AddressData = await GetNmProp(i.ip6_config_path, "IP6Config", "AddressData")

        i.Ip4 = addressDataToString(ip4AddressData)
        i.Ip6 = addressDataToString(ip6AddressData)

        i.Status = combineAddresses(ip4AddressData, ip6AddressData)

    return i


def GetIp(version: str, settings: dict) -> Ipv4v6:

    ip = Ipv4v6()

    ip_settings = settings.get(version)

    ip_settings: dict
    if ip_settings:
        addrData = ip_settings.get("address-data")
        if addrData:
            for addr in addrData.value:
                a = addr.get("address").value
                p = addr.get("prefix").value
                ip.AddressData.append(IpAddress(a, p))

        dnsData = ip_settings.get("dns-data")
        if dnsData:
            for dns in dnsData.value:
                ip.DnsData.append(DnsServer(dns))

        dnsSearch = ip_settings.get("dns-search")
        if dnsSearch:
            for dns in dnsSearch.value:
                ip.DnsSearch.append(DnsServer(dns))

        gateway = ip_settings.get("gateway")
        if gateway:
            ip.Gateway = gateway.value

        ignoreAutoDns = ip_settings.get("ignore-auto-dns")
        if ignoreAutoDns:
            ip.IgnoreAutoDns = ignoreAutoDns.value

        ignoreAutoRoutes = ip_settings.get("ignore-auto-routes")
        if ignoreAutoRoutes:
            ip.IgnoreAutoRoutes = ignoreAutoRoutes.value

        method = ip_settings.get("method")
        if method:
            ip.Method = method.value

        routeData = ip_settings.get("route-data")
        if routeData:
            for route in routeData.value:
                a = route.get("dest").value
                p = route.get("prefix").value
                n = route.get("next-hop").value
                m = route.get("metric").value
                ip.RouteData.append(IpRoute(a, p, n, m))

    return ip


def SetIp(ip: Ipv4v6, version: str, settings: dict) -> dict:

    # remove depreciated
    settings[version].pop("addresses", None)
    settings[version].pop("dns", None)
    settings[version].pop("routes", None)

    # address data
    settings[version]["address-data"] = addresses_to_dbus(ip.AddressData)
    # dns data
    settings[version]["dns-data"] = dns_to_dbus(ip.DnsData)
    # dns search
    settings[version]["dns-search"] = dns_to_dbus(ip.DnsSearch)
    # gateway
    settings[version]["gateway"] = Variant("s", ip.Gateway)
    # ignore auto dns
    settings[version]["ignore-auto-dns"] = Variant("b", (ip.IgnoreAutoDns))
    # ignore auto routes
    settings[version]["ignore-auto-routes"] = Variant("b", (ip.IgnoreAutoRoutes))
    # method
    settings[version]["method"] = Variant("s", ip.Method)
    # route data
    settings[version]["route-data"] = route_to_dbus(ip.RouteData)

    return settings


def addresses_to_dbus(ip: list[IpAddress]):
    return Variant(
        "aa{sv}",
        [
            {"address": Variant("s", i.Address), "prefix": Variant("u", int(i.Prefix))}
            for i in ip
        ],
    )


def dns_to_dbus(dns: list[DnsServer]):
    return Variant("as", [d.Server for d in dns])


def route_to_dbus(route: list[IpRoute]):
    return Variant(
        "aa{sv}",
        [
            {
                "dest": Variant("s", r.Dest),
                "prefix": Variant("u", int(r.Prefix)),
                "next-hop": Variant("s", r.NextHop),
                "metric": Variant("u", int(r.Metric)),
            }
            for r in route
        ],
    )


def ApplyModes(version: str, settings: dict) -> dict:

    if settings[version]["method"].value == "auto":
        settings[version].pop("gateway", None)

    if settings[version]["method"].value == "disabled":
        settings[version].pop("gateway", None)

    return settings


def addressDataToAddress(addressdata: list[dict]) -> list:
    formatted = []
    for addr in addressdata:
        address = addr.get("address").value
        prefix = addr.get("prefix").value
        if address and prefix:
            formatted.append(f"{address}/{prefix}")
    return formatted


def formatAddressString(addresses: list[str]) -> str:
    return ", ".join(addresses) if addresses else ""


def formatInterfaceRow(interface: str, addresses: str):
    return {"name": interface, "addresses": addresses}


def addressDataToString(addressData):
    addresses = []
    addresses.extend(addressDataToAddress(addressData))
    if len(addresses) == 0:
        return "disabled"
    return formatAddressString(addresses)


def dnsDataToString(dnsData):
    return formatAddressString(dnsData)


def processDeviceState(state: int) -> str:
    state_dict = {
        0: ["UNKNOWN", "the device's state is unknown"],
        10: [
            "UNMANAGED",
            "the device is recognized, but not managed by NetworkManager",
        ],
        20: [
            "UNAVAILABLE",
            "the device is managed by NetworkManager, but is not available for use. Reasons may include the wireless switched off, missing firmware, no ethernet carrier, missing supplicant or modem manager, etc.",
        ],
        30: [
            "DISCONNECTED",
            "the device can be activated, but is currently idle and not connected to a network.",
        ],
        40: [
            "PREPARE",
            "the device is preparing the connection to the network. This may include operations like changing the MAC address, setting physical link properties, and anything else required to connect to the requested network.",
        ],
        50: [
            "CONFIG",
            "the device is connecting to the requested network. This may include operations like associating with the Wi-Fi AP, dialing the modem, connecting to the remote Bluetooth device, etc.",
        ],
        60: [
            "NEED_AUTH",
            "the device requires more information to continue connecting to the requested network. This includes secrets like WiFi passphrases, login passwords, PIN codes, etc.",
        ],
        70: [
            "IP_CONFIG",
            "the device is requesting IPv4 and/or IPv6 addresses and routing information from the network.",
        ],
        80: [
            "IP_CHECK",
            "the device is checking whether further action is required for the requested network connection. This may include checking whether only local network access is available, whether a captive portal is blocking access to the Internet, etc.",
        ],
        90: [
            "SECONDARIES",
            "the device is waiting for a secondary connection (like a VPN) which must activated before the device can be activated",
        ],
        100: [
            "ACTIVATED",
            "the device has a network connection, either local or global.",
        ],
        110: [
            "DEACTIVATING",
            "a disconnection from the current network connection was requested, and the device is cleaning up resources used for that connection. The network connection may still be valid.",
        ],
        120: [
            "FAILED",
            "the device failed to connect to the requested network and is cleaning up the connection request",
        ],
    }
    nmState = state_dict.get(state, "STATE NOT FOUND")
    return nmState[0]


def processInterfaceFlags(flags: int) -> str:
    # NM_DEVICE_INTERFACE_FLAG_NONE = 0  # an alias for numeric zero, no flags set.
    NM_DEVICE_INTERFACE_FLAG_UP = 0x1  # the interface is enabled from the administrative point of view. Corresponds to kernel IFF_UP.
    NM_DEVICE_INTERFACE_FLAG_LOWER_UP = (
        0x2  # the physical link is up. Corresponds to kernel IFF_LOWER_UP.
    )
    NM_DEVICE_INTERFACE_FLAG_PROMISC = (
        0x4  # receive all packets. Corresponds to kernel IFF_PROMISC. Since: 1.32.
    )
    NM_DEVICE_INTERFACE_FLAG_CARRIER = 0x10000  # the interface has carrier. In most cases this is equal to the value of @NM_DEVICE_INTERFACE_FLAG_LOWER_UP. However some devices have a non-standard carrier detection mechanism.
    NM_DEVICE_INTERFACE_FLAG_LLDP_CLIENT_ENABLED = (
        0x20000  # the flag to indicate device LLDP status. Since: 1.32.
    )
    """Convert interface flags to detailed status string"""

    if flags == 0:
        return "Interface disabled (no flags set)"

    status = []

    if flags & NM_DEVICE_INTERFACE_FLAG_UP:
        status.append("administratively up")

    if flags & NM_DEVICE_INTERFACE_FLAG_LOWER_UP:
        status.append("physical link up")

    if flags & NM_DEVICE_INTERFACE_FLAG_CARRIER:
        status.append("carrier detected")

    if flags & NM_DEVICE_INTERFACE_FLAG_PROMISC:
        status.append("promiscuous mode")

    if flags & NM_DEVICE_INTERFACE_FLAG_LLDP_CLIENT_ENABLED:
        status.append("LLDP enabled")

    if not status:
        return f"Unknown flags: 0x{flags:x}"

    return " | ".join(status)


def combineAddresses(ipv4AddressData, ipv6AddressData) -> str:

    addresses = []
    addresses.extend(addressDataToAddress(ipv4AddressData))
    addresses.extend(addressDataToAddress(ipv6AddressData))
    return formatAddressString(addresses)


async def GetDeviceFromInterface(iface: str) -> Device:

    device_path = await GetDeviceByIpIface(iface)

    hwaddr = await GetNmProp(device_path, "Device", "HwAddress")
    flags = await GetNmProp(device_path, "Device", "InterfaceFlags")
    carrier = processInterfaceFlags(flags)
    state = await GetNmProp(device_path, "Device", "State")
    deviceState = processDeviceState(state)
    ip4_config_path = await GetNmProp(device_path, "Device", "IP6Config")
    ip6_config_path = await GetNmProp(device_path, "Device", "IP6Config")

    active_connection_path = await GetNmProp(device_path, "Device", "ActiveConnection")

    myDevice = Device(
        Path=device_path,
        ActiveConnectionPath=active_connection_path,
        HardwareAddress=hwaddr,
        Flags=flags,
        Carrier=carrier,
        State=state,
        DeviceState=deviceState,
        Ip4ConfigPath=ip4_config_path,
        Ip6ConfigPath=ip6_config_path,
    )

    return myDevice


def isAutoconnect(settings: dict) -> bool:
    return settings["connection"]


async def GetInterfaces() -> list:

    interfaces = []

    devices_paths = await GetDevices()

    for p in devices_paths:
        deviceType = await GetNmProp(p, "Device", "DeviceType")
        iface = await GetNmProp(p, "Device", "Interface")
        if deviceType not in [1]:
            continue
        interfaces.append(iface)

    return interfaces


async def GetInterfacesAndAddresses() -> list:

    rows = []

    device_paths = await GetDevices()

    for devicePath in device_paths:

        interface = await GetNmProp(devicePath, "Device", "Interface")
        hwaddr = await GetNmProp(devicePath, "Device", "HwAddress")
        state = await GetNmProp(devicePath, "Device", "State")
        deviceType = await GetNmProp(devicePath, "Device", "DeviceType")

        if deviceType not in [1]:  # // wired types only
            continue
        # processDeviceState
        ip4_config_path = await GetNmProp(devicePath, "Device", "Ip4Config")
        ip6_config_path = await GetNmProp(devicePath, "Device", "Ip6Config")

        log.info(f"IP 4 CONFIG PATH: {ip4_config_path}")

        if len(ip4_config_path) > 1:

            ip4AddressData = await GetNmProp(
                ip4_config_path, "IP4Config", "AddressData"
            )
            ip6AddressData = await GetNmProp(
                ip6_config_path, "IP6Config", "AddressData"
            )

            gw = []
            ip4gw = await GetNmProp(ip4_config_path, "IP4Config", "Gateway")
            if ip4gw:
                gw.append(ip4gw)
            ip6gw = await GetNmProp(ip6_config_path, "IP6Config", "Gateway")
            if ip6gw:
                gw.append(ip4gw)

            rows.append(
                {
                    "name": interface,
                    "addresses": combineAddresses(ip4AddressData, ip6AddressData),
                    "state": processDeviceState(state),
                    "gateway": formatListToString(gw),
                    "hw address": hwaddr,
                }
            )

    return rows
