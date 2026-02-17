
from dataclasses import asdict, field
from typing import List, Optional
from nicegui import ui, app, binding

from dbus_next.signature import Variant
from dbus_next.errors import DBusError
from dbus_next.aio.proxy_object import ProxyInterface
from dbus_next.aio import MessageBus
from dbus_next import Message

from ns2.firewalld import formatListToString
from ns2.utils import INTROSPECTION_DIR

# ====================================================================
# data classes
# ====================================================================

class ConnectionDetails:
    Id:          Optional[str] = ''
    Permissions: Optional[list[str]] = None
    Timestamp:   Optional[int] = 0
    Type:        Optional[str] = ''
    Uuid:        Optional[str] = ''

@binding.bindable_dataclass
class IpAddress:
    Address: Optional[str] = None
    Prefix: Optional[int] = None

@binding.bindable_dataclass
class DnsServer:
    Server: Optional[str] = ''

@binding.bindable_dataclass
class IpRoute:
    Dest: Optional[str] = None
    Prefix: Optional[int] = None
    NextHop: Optional[str] = None
    Metric: Optional[int] = None


@binding.bindable_dataclass
class Ipv4v6:
    AddressData:      Optional[list[IpAddress]] = field(default_factory=list) # used
    #Addresses:        Optional[list[list[int]]] = field(default_factory=list) # not used
    #Dns:              Optional[list[list[int]]] = field(default_factory=list) # not used
    DnsData:          Optional[list[DnsServer]] = field(default_factory=list) # used
    DnsSearch:        Optional[list[DnsServer]] = field(default_factory=list) # used 
    Gateway:          Optional[str] = ''                                      # used
    IgnoreAutoDns:    Optional[bool] = False                                  # used 
    IgnoreAutoRoutes: Optional[bool] = False                                  # used
    Method:           Optional[str] = ''                                      # used
    RouteData:        Optional[list[IpRoute]] = field(default_factory=list)   # used
    #Routes:           Optional[list[list[int]]] = field(default_factory=list) # not used


@binding.bindable_dataclass
class Settings:
    Connection: Optional[ConnectionDetails] = None
    Ipv4:       Optional[Ipv4v6] = None
    Ipv6:       Optional[Ipv4v6] = None
    Proxy:      Optional[str]  = ''


@binding.bindable_dataclass
class Device:
    Proxy:           Optional[ProxyInterface] = None
    Path:            Optional[str] = ''
    ActiveConnectionPath: Optional[str] = ''
    HardwareAddress: Optional[str] = ''
    Flags:           Optional[int] = None
    Carrier:         Optional[str] = ''
    State:           Optional[int] = True
    DeviceState:     Optional[str] = ''
    Ip4ConfigPath :  Optional[str] = ''
    Ip6ConfigPath :  Optional[str] = ''


@binding.bindable_dataclass
class InterfaceData:
    Name:               Optional[str] = ''
    HardwareAddress:    Optional[str] = ''
    StateString:        Optional[str] = ''
    StateNumber:        Optional[int] = 0
    Active:             Optional[bool] = False
    Status:             Optional[str] = ''
    Carrier:            Optional[str] = ''
    Ip4:                Optional[str] = ''
    Ip6:                Optional[str] = ''
    AutoConnect:        Optional[bool] = False
    _dev_path:          Optional[str] = ''
    _act_con_path:      Optional[str] = ''



# ====================================================================
# Proxies
# ====================================================================
def GetNetworkManager(bus: MessageBus) -> ProxyInterface:
    file_name = 'org.freedesktop.NetworkManager.xml'
    with open(str(INTROSPECTION_DIR /file_name), "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager', introspection)
    return obj.get_interface('org.freedesktop.NetworkManager')


def GetDevice(bus: MessageBus, path :str) -> ProxyInterface:
    file_name = 'org.freedesktop.NetworkManager.Device.xml'
    with open(str(INTROSPECTION_DIR /file_name), "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspection)
    return obj.get_interface('org.freedesktop.NetworkManager.Device')


def GetActiveConnection(bus: MessageBus, path :str) -> ProxyInterface:
    file_name = 'org.freedesktop.NetworkManager.Connection.Active.xml'
    with open(str(INTROSPECTION_DIR /file_name), "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspection)
    return obj.get_interface('org.freedesktop.NetworkManager.Connection.Active')


def GetIp4Config(bus: MessageBus, path :str) -> ProxyInterface:
    file_name = 'org.freedesktop.NetworkManager.IP4Config.xml'
    with open(str(INTROSPECTION_DIR /file_name), "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspection)
    return obj.get_interface('org.freedesktop.NetworkManager.IP4Config')

def GetIp6Config(bus: MessageBus, path :str) -> ProxyInterface:
    file_name = 'org.freedesktop.NetworkManager.IP6Config.xml'
    with open(str(INTROSPECTION_DIR /file_name), "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspection)
    return obj.get_interface('org.freedesktop.NetworkManager.IP6Config')


def GetSettingsManager(bus: MessageBus, path :str) -> ProxyInterface:
    file_name = 'org.freedesktop.NetworkManager.Settings.xml'
    with open(str(INTROSPECTION_DIR /file_name), "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspection)
    return obj.get_interface('org.freedesktop.NetworkManager.Settings')

def GetConnection(bus: MessageBus, path : str)-> ProxyInterface:
    file_name = 'org.freedesktop.NetworkManager.Settings.Connection.xml'
    with open(str(INTROSPECTION_DIR /file_name), "r") as f:
        introspection = f.read()
    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspection)
    return obj.get_interface('org.freedesktop.NetworkManager.Settings.Connection')


async def GetConnectionFromDevice(bus: MessageBus, device :ProxyInterface) -> ProxyInterface:
    active_connection_path = await device.get_active_connection()
    if len(active_connection_path) > 1:
        activeConnection = GetActiveConnection(bus, active_connection_path)
        connection_path = await activeConnection.get_connection()
        return GetConnection(bus, connection_path)
    
    
# ====================================================================
# Getters and Setters
# ====================================================================

async def GetInterfaceData(bus: MessageBus, nm: ProxyInterface, iface :str) -> InterfaceData:
    i = InterfaceData()
    i._dev_path = await nm.call_get_device_by_ip_iface(iface)
    dev = GetDevice(bus, i._dev_path)
    i.Name = iface
    i.HardwareAddress = await dev.get_hw_address()
    i.StateNumber = await dev.get_state()
    i.StateString = processDeviceState(i.StateNumber)
    i.Active = True if i.StateNumber == 100 else False
    i.Carrier = processInterfaceFlags(await dev.get_interface_flags())

    ip4_config_path = await dev.get_ip4_config()
    ip6_config_path = await dev.get_ip6_config()

    i._act_con_path = await dev.get_active_connection()

    if len(i._act_con_path) > 1:
        activeConnection = GetActiveConnection(bus, i._act_con_path)
        connection_path = await activeConnection.get_connection()
        connection = GetConnection(bus, connection_path)
        settings = await connection.call_get_settings()
        i.AutoConnect = settings['connection'].get('autoconnect', Variant('b', True)).value


    if len(ip4_config_path) > 1:
        ip4Config = GetIp4Config(bus, ip4_config_path)
        ip6Config = GetIp6Config(bus, ip6_config_path)
        ip4AddressData = await ip4Config.get_address_data()
        ip6AddressData = await ip6Config.get_address_data()
        i.Ip4 = addressDataToString(ip4AddressData)
        i.Ip6 = addressDataToString(ip6AddressData)

        i.Status = combineAddresses(ip4AddressData, ip6AddressData)

    return i


async def GetSettings(bus: MessageBus, dev: ProxyInterface) -> dict:
    active_connection_path = await dev.get_active_connection()
    if len(active_connection_path) > 1:
        activeConnection = GetActiveConnection(bus, active_connection_path)
        connection_path = await activeConnection.get_connection()
        connection = GetConnection(bus, connection_path)
        connection_settings = await connection.call_get_settings()
    return connection_settings





def GetIp(version: str, settings: dict) -> Ipv4v6:

    ip = Ipv4v6()

    ip_settings = settings.get(version)

    ip_settings: dict
    if ip_settings:    
        addrData = ip_settings.get('address-data')
        if addrData:
            for addr in addrData.value:
                a = addr.get('address').value
                p = addr.get('prefix').value
                ip.AddressData.append(IpAddress(a, p))
        
        dnsData = ip_settings.get('dns-data')
        if dnsData:
            for dns in dnsData.value:
                ip.DnsData.append(DnsServer(dns))
        
        dnsSearch = ip_settings.get('dns-search')
        if dnsSearch:
            for dns in dnsSearch.value:
                ip.DnsSearch.append(DnsServer(dns))

        gateway = ip_settings.get('gateway')
        if gateway:
            ip.Gateway = gateway.value

        ignoreAutoDns = ip_settings.get('ignore-auto-dns')
        if ignoreAutoDns:
            ip.IgnoreAutoDns = ignoreAutoDns.value

        
        ignoreAutoRoutes = ip_settings.get('ignore-auto-routes')
        if ignoreAutoRoutes:
            ip.IgnoreAutoRoutes = ignoreAutoRoutes.value

        method = ip_settings.get('method')
        if method:
            ip.Method = method.value
        

        routeData = ip_settings.get('route-data')
        if routeData:
            for route in routeData.value:
                a = route.get('dest').value
                p = route.get('prefix').value
                n = route.get('next-hop').value
                m = route.get('metric').value
                ip.RouteData.append(IpRoute(a, p, n, m))

    return ip



def SetIp(ip: Ipv4v6, version: str, settings :dict) -> dict:

    #remove depreciated 
    settings[version].pop("addresses", None)
    settings[version].pop("dns", None)
    settings[version].pop("routes", None)

    # address data
    settings[version]['address-data'] = addresses_to_dbus(ip.AddressData)
    # dns data
    settings[version]['dns-data'] = dns_to_dbus(ip.DnsData)
    # dns search
    settings[version]['dns-search'] = dns_to_dbus(ip.DnsSearch)
    # gateway
    settings[version]['gateway'] = Variant('s', ip.Gateway)
    # ignore auto dns
    settings[version]['ignore-auto-dns'] = Variant('b',  ( ip.IgnoreAutoDns))
    # ignore auto routes
    settings[version]['ignore-auto-routes'] = Variant('b', ( ip.IgnoreAutoRoutes))
    # method  
    settings[version]['method'] = Variant('s', ip.Method)
    #route data
    settings[version]['route-data'] = route_to_dbus(ip.RouteData)

    return settings




def addresses_to_dbus(ip :list[IpAddress]):
    return Variant('aa{sv}', [{'address': Variant('s', i.Address), 'prefix': Variant('u', int(i.Prefix))} for i in ip])

def dns_to_dbus(dns :list[DnsServer]):
    return Variant('as', [d.Server for d in dns])

def route_to_dbus(route: list[IpRoute]):
    return Variant('aa{sv}', [{'dest': Variant('s', r.Dest), 
                               'prefix': Variant('u', int(r.Prefix)),
                               'next-hop': Variant('s', r.NextHop),
                               'metric': Variant('u', int(r.Metric)),
                               } for r in route])



def ApplyModes(version :str, settings :dict) -> dict:

    if settings[version]['method'].value == 'auto':
        settings[version].pop('gateway', None)
    
    if settings[version]['method'].value == 'disabled':
        settings[version].pop('gateway', None)
    
    return settings

    
    


def addressDataToAddress(addressdata: list[dict]) -> list:
    formatted = []
    for addr in addressdata:
        address = addr.get('address')
        prefix = addr.get('prefix')
        if address and prefix:
            formatted.append(f"{address.value}/{prefix.value}")
    return formatted


def formatAddressString(addresses: list[str]) -> str:
    return ', '.join(addresses) if addresses else ''

def formatInterfaceRow(interface :str, addresses: str):
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
    state_dict = {0:  ["UNKNOWN",        "the device's state is unknown"],
                 10:  ["UNMANAGED",     "the device is recognized, but not managed by NetworkManager"],
                 20:  ["UNAVAILABLE",   "the device is managed by NetworkManager, but is not available for use. Reasons may include the wireless switched off, missing firmware, no ethernet carrier, missing supplicant or modem manager, etc."],
                 30:  ["DISCONNECTED",  "the device can be activated, but is currently idle and not connected to a network."],
                 40:  ["PREPARE",       "the device is preparing the connection to the network. This may include operations like changing the MAC address, setting physical link properties, and anything else required to connect to the requested network."],
                 50:  ["CONFIG",        "the device is connecting to the requested network. This may include operations like associating with the Wi-Fi AP, dialing the modem, connecting to the remote Bluetooth device, etc."],
                 60:  ["NEED_AUTH",     "the device requires more information to continue connecting to the requested network. This includes secrets like WiFi passphrases, login passwords, PIN codes, etc."],
                 70:  ["IP_CONFIG",     "the device is requesting IPv4 and/or IPv6 addresses and routing information from the network."],
                 80:  ["IP_CHECK",      "the device is checking whether further action is required for the requested network connection. This may include checking whether only local network access is available, whether a captive portal is blocking access to the Internet, etc."],
                 90:  ["SECONDARIES",   "the device is waiting for a secondary connection (like a VPN) which must activated before the device can be activated"],
                 100: ["ACTIVATED",    "the device has a network connection, either local or global."],
                 110: ["DEACTIVATING", "a disconnection from the current network connection was requested, and the device is cleaning up resources used for that connection. The network connection may still be valid."],
                 120: ["FAILED",       "the device failed to connect to the requested network and is cleaning up the connection request"]}
    nmState = state_dict.get(state, "STATE NOT FOUND")
    return nmState[0]


def processInterfaceFlags(flags: int) -> str:
    NM_DEVICE_INTERFACE_FLAG_NONE= 0 # an alias for numeric zero, no flags set. 
    NM_DEVICE_INTERFACE_FLAG_UP= 0x1 # the interface is enabled from the administrative point of view. Corresponds to kernel IFF_UP. 
    NM_DEVICE_INTERFACE_FLAG_LOWER_UP= 0x2 # the physical link is up. Corresponds to kernel IFF_LOWER_UP. 
    NM_DEVICE_INTERFACE_FLAG_PROMISC= 0x4 # receive all packets. Corresponds to kernel IFF_PROMISC. Since: 1.32. 
    NM_DEVICE_INTERFACE_FLAG_CARRIER= 0x10000 # the interface has carrier. In most cases this is equal to the value of @NM_DEVICE_INTERFACE_FLAG_LOWER_UP. However some devices have a non-standard carrier detection mechanism. 
    NM_DEVICE_INTERFACE_FLAG_LLDP_CLIENT_ENABLED= 0x20000 # the flag to indicate device LLDP status. Since: 1.32.
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




async def GetDeviceFromInterface(bus: MessageBus, iface :str) -> Device:
    nm = GetNetworkManager(bus)
    device_path = await nm.call_get_device_by_ip_iface(iface)
    device = GetDevice(bus, device_path)

    hwaddr = await device.get_hw_address()
    flags = await device.get_interface_flags()
    carrier = processInterfaceFlags(flags)

    state = await device.get_state()
    deviceState = processDeviceState(state)
    ip4_config_path = await device.get_ip4_config()
    ip4_config_path = await device.get_ip6_config()
    active_connection_path = await device.get_active_connection()

    myDevice = Device(
    Proxy = device,
    Path = device_path,
    ActiveConnectionPath = active_connection_path,
    HardwareAddress = hwaddr,
    Flags = flags,
    Carrier = carrier,
    State = state,
    DeviceState = deviceState,
    Ip4ConfigPath = ip4_config_path,
    Ip6ConfigPath = ip4_config_path)

    return myDevice



def isAutoconnect(settings :dict) -> bool:
    return settings['connection']



async def GetInterfaces(bus: MessageBus) -> list:

    interfaces = []

    nm = GetNetworkManager(bus)

    devices_paths = await nm.call_get_devices()

    for p in devices_paths:
        dev = GetDevice(bus, p)
        interfaces.append(await dev.get_interface())
    
    return interfaces

async def GetInterfacesAndAddresses(bus: MessageBus) -> list:

    rows = []

    nm = GetNetworkManager(bus)
    
    device_paths = await nm.call_get_devices()
    
    for devicePath in device_paths:

        device = GetDevice(bus, devicePath)
        interface = await device.get_interface()
        hwaddr = await device.get_hw_address()
        state = await device.get_state()
        processDeviceState
        ip4_config_path = await device.get_ip4_config()
        ip6_config_path = await device.get_ip6_config()
        if len(ip4_config_path) > 1:

            ip4Config = GetIp4Config(bus, ip4_config_path)
            ip6Config = GetIp6Config(bus, ip6_config_path)

            ip4AddressData = await ip4Config.get_address_data()
            ip6AddressData = await ip6Config.get_address_data()

            gw = []
            ip4gw = await ip4Config.get_gateway()
            if ip4gw:
                gw.append(ip4gw)
            ip6gw = await ip6Config.get_gateway()
            if ip6gw:
                gw.append(ip4gw)


    
            rows.append({'name': interface,
                         'addresses': combineAddresses(ip4AddressData, ip6AddressData),
                         'state':processDeviceState(state),
                         'gateway': formatListToString(gw),
                         'hw address': hwaddr})
        
    return rows


async def nm_call(bus: MessageBus, member: str, signature:str, body):

    rsp = await bus.call(
        Message(
            destination='org.freedesktop.NetworkManager',
            path='/org/freedesktop/NetworkManager',
            interface='org.freedesktop.NetworkManager',
            member=member,
            signature=signature,
            body=[body]
        )
    )
    
    if rsp.body:
        return rsp.body[0]