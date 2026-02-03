import asyncio
from dataclasses import asdict, field
from pprint import pprint
from typing import List, Optional
from nicegui import ui, app, binding
from ns.lib.commands import runCmd
from ns.ui.theme import init_colors


from dbus_next.signature import Variant
from dbus_next.errors import DBusError
from dbus_next.aio.proxy_object import ProxyInterface
from dbus_next.aio import MessageBus
from dbus_next import Message
from ns.dbus import dbus
from ns.utils import INTROSPECTION_DIR


@binding.bindable_dataclass
class ServiceSetting:
    Version:           Optional[str] = ''
    Name:              Optional[str] = ''
    Description:       Optional[str] = ''
    Ports:             Optional[list[str]]  = field(default_factory=list)
    ModuleNames:       Optional[list[str]] = field(default_factory=list)
    Destinations:      Optional[dict] = field(default_factory=dict)
    Protocols:         Optional[list[str]] = field(default_factory=list)
    SourcePorts:       Optional[list[str]] = field(default_factory=list)
    Includes:          Optional[list[str]] = field(default_factory=list)
    Helpers:           Optional[list[str]] = field(default_factory=list)


@binding.bindable_dataclass
class ZoneSetting:
    Description:       Optional[str] = ''
    Interfaces:        Optional[list[str]] = field(default_factory=list)
    Services:          Optional[list[str]] = field(default_factory=list)
    Short:             Optional[str] = ''
    ServiceSettings:   Optional[dict[ServiceSetting]] = field(default_factory=dict)
    Sources:           Optional[list[str]] = field(default_factory=list)
    
    
@binding.bindable_dataclass
class Firewall:
    Enable:            Optional[bool] = False
    Status:            Optional[str] = ''
    ActiveZones:       Optional[dict[dict]] = field(default_factory=dict)
    AllowedAddresses:  Optional[list[str]] = field(default_factory=list)
    Services:          Optional[dict[dict]] = field(default_factory=dict)
    ZoneSettings:      Optional[dict[ZoneSetting]] = field(default_factory=dict)


async def GetFirewalld(bus: MessageBus):
    file_name = 'org.fedoraproject.FirewallD1.config.xml'
    introspection = await bus.introspect('org.fedoraproject.FirewallD1', '/org/fedoraproject/FirewallD1')
    #pprint(introspection.tostring())
    obj = bus.get_proxy_object('org.fedoraproject.FirewallD1', '/org/fedoraproject/FirewallD1', introspection)
    return obj.get_interface('org.fedoraproject.FirewallD1')

async def GetFirewalldConfig(bus: MessageBus):
    file_name = 'org.fedoraproject.FirewallD1.config.xml'
    introspection = await bus.introspect('org.fedoraproject.FirewallD1', '/org/fedoraproject/FirewallD1/config')
    #pprint(introspection.tostring())
    obj = bus.get_proxy_object('org.fedoraproject.FirewallD1', '/org/fedoraproject/FirewallD1/config', introspection)
    return obj.get_interface('org.fedoraproject.FirewallD1.config')



async def GetFirewalldConfigZone(bus: MessageBus, path : str):
    introspection = await bus.introspect('org.fedoraproject.FirewallD1', path)
    obj = bus.get_proxy_object('org.fedoraproject.FirewallD1', path, introspection)
    return obj.get_interface('org.fedoraproject.FirewallD1.config.zone')

#def GetDevice(bus: MessageBus, path : str):
#    file_name = 'org.freedesktop.NetworkManager.Device.xml'
#    with open(str(INTROSPECTION_DIR /file_name), "r") as f:
#        introspection = f.read()
#    obj = bus.get_proxy_object('org.freedesktop.NetworkManager', path, introspection)
#    return obj.get_interface('org.freedesktop.NetworkManager.Device')

async def GetFirewalldZone(bus: MessageBus):
    file_name = 'org.fedoraproject.FirewallD1.zone.xml'
    introspection = await bus.introspect('org.fedoraproject.FirewallD1', '/org/fedoraproject/FirewallD1')
    #pprint(introspection.tostring())
    obj = bus.get_proxy_object('org.fedoraproject.FirewallD1', '/org/fedoraproject/FirewallD1', introspection)
    return obj.get_interface('org.fedoraproject.FirewallD1.zone')




def formatListToString(elements: list[str]) -> str:
    if len(elements) == 0:
        return None
    return ', '.join(elements) if elements else ''

def getZoneInfo(name :str, zone :dict) -> dict:

    interfaces = formatListToString(zone.get('interfaces', []))
    sources = formatListToString(zone.get('sources', []))

    return {'name':name, 'interfaces':interfaces, 'sources':sources}


async def getServices(bus: MessageBus):
    '''all not just runtime'''

    fire = await GetFirewalld(bus)
#
    #conf = await GetFirewalldConfig(bus)
    
    #serviceNames = await conf.call_get_service_names()

    rsp = await bus.call(
        Message(
            destination='org.fedoraproject.FirewallD1',
            path='/org/fedoraproject/FirewallD1/config',
            interface='org.fedoraproject.FirewallD1.config',
            member='getServiceNames',
            signature='',
            body=""
        )
    )
    
    serviceNames = rsp.body[0]
    

    services = {}
    for name in serviceNames:
        s = ServiceSetting()
        s.Name = name
        serviceSettings = await fire.call_get_service_settings2(s.Name)
                                
        includes = serviceSettings.get('includes', False)
        if includes:
            for i in includes.value:
                ser_set = await fire.call_get_service_settings2(i)
                s.Ports.extend(ser_set.get('ports', Variant('a(ss)', [['port not available', 'protocol not available']])).value)

                            
        s.Name = serviceSettings.get('short', Variant('s', 'name not available')).value
        s.Ports.extend(serviceSettings.get('ports', Variant('a(ss)', [['port not available', 'protocol not available']])).value)
        s.Description = serviceSettings.get('description', Variant('s', 'Description not available')).value

        services[name] = s


    return services



#async def addZone2(bus: MessageBus, interface: str, services: list[str]):
#    
#    conf = await GetFirewalldConfig(bus)
#    _settings = {
#        "version":"0"
#        
#        
#        "version": ""
#        "name"  (s): see
#        "description"  (s): see
#        "target"  (s): see
#        "services"  (as): services
#        "ports"  (a(ss)):
#        "icmp_blocks"  (as): array
#        "masquerade"  (b): see
#        "forward_ports"  (a(ssss)):
#        "interfaces"  (as): array
#        "sources"  (as): []
#        "rules_str"  (as): []
#        "protocols"  (as): []
#        "source_ports" : []
#        "icmp_block_inversion" : False
#        "forward" : False
#        
#    }
#    
#    
#
#    
#    
#    newZonePath = await conf.call_add_zone_2()
#    



def getUdpPorts(ports) -> list:
    out = []
    for p in ports:
        if p[1]=='udp':
            out.append(p[0])

    return formatListToString(out)

def getTcpPorts(ports) -> list:
    out = []
    for p in ports:
        if p[1]=='tcp':
            out.append(p[0])

    return formatListToString(out)
    


def formatServicesInRows(serviceSettings :dict):
    

    rows = []
    for n, s in serviceSettings.items():
        rows.append({ 
                     #"Select": False,
                     "Service": n
                     ,"UDP": getUdpPorts(s.Ports)
                     ,"TCP": getTcpPorts(s.Ports)
                     ,"Description": s.Description
                     #,"remove": ''
                     })
        
    #pprint(rows)
    return rows