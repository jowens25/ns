import asyncio
from dataclasses import asdict, field
from pprint import pprint
from typing import List, Optional
from nicegui import ui, app, binding
from ns2.commands import runCmd
from ns2.theme import init_colors
from ns2.networking import GetInterfaces

from ns2.common import formatListToString

from dbus_next.signature import Variant
from dbus_next.errors import DBusError
from dbus_next.aio.proxy_object import ProxyInterface
from dbus_next.aio import MessageBus
from dbus_next import Message
import ns2.dbus
from ns2.utils import INTROSPECTION_DIR


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
class ZoneInfo:
    Description:       Optional[str] = ''
    Interfaces:        Optional[list[str]] = field(default_factory=list)
    Services:          Optional[list[str]] = field(default_factory=list)
    Short:             Optional[str] = ''
    Name:              Optional[str] = ''
    ServiceSettings:   Optional[dict[ServiceSetting]] = field(default_factory=dict)
    Sources:           Optional[list[str]] = field(default_factory=list)
    
    
@binding.bindable_dataclass
class FirewallInfo:
    Enable:            Optional[bool] = False
    Status:            Optional[str] = ''
    ActiveZones:       Optional[dict[dict]] = field(default_factory=dict)
    AllowedAddresses:  Optional[list[str]] = field(default_factory=list)
    Services:          Optional[dict[dict]] = field(default_factory=dict)
    ZoneInfos:             Optional[dict[ZoneInfo]] = field(default_factory=dict)





async def zoneRemoveService(bus: MessageBus, zoneName: str, serviceName:str):
    rsp = await bus.call(
    Message(
        destination='org.fedoraproject.FirewallD1',
        path='/org/fedoraproject/FirewallD1',
        interface='org.fedoraproject.FirewallD1.zone',
        member='removeService',
        signature='ss',
        body=[zoneName, serviceName]
        )
    )
    
    return rsp.body[0]

async def zoneConfigRemoveService(bus: MessageBus, zonePath: str, serviceName:str):
    rsp = await bus.call(
    Message(
        destination='org.fedoraproject.FirewallD1',
        path=zonePath,
        interface='org.fedoraproject.FirewallD1.config.zone',
        member='removeService',
        signature='s',
        body=[serviceName]
        )
    )
    
    return rsp.body[0]



async def GetActiveZones(bus: MessageBus) -> list[ZoneInfo]:
    rsp = await bus.call(
        Message(
            destination='org.fedoraproject.FirewallD1',
            path='/org/fedoraproject/FirewallD1',
            interface='org.fedoraproject.FirewallD1.zone',
            member='getActiveZones',
            signature='',
            body=[]
        )
    )
    
    return rsp.body[0]


async def GetZones(bus: MessageBus) -> list[ZoneInfo]:
    rsp = await bus.call(
        Message(
            destination='org.fedoraproject.FirewallD1',
            path='/org/fedoraproject/FirewallD1',
            interface='org.fedoraproject.FirewallD1.zone',
            member='getZones',
            signature='',
            body=[]
        )
    )

    return rsp.body[0]

#Sorted from least to most trusted
#
#external
#dmz
#work
#home
#internal

async def GetSelectableZones(bus: MessageBus):
    default_zones = [
        "public",
        "external",
        "dmz",
        "work",
        "home",
        "internal"]
    available_zones = []
    allzones = await GetZones(bus)
    actzones = await GetActiveZones(bus)
    for z in allzones:
        print(z)
        if (z in default_zones) and (z not in actzones):
            available_zones.append(z)
            
    return available_zones

async def GetZoneInfo(bus: MessageBus, zoneName: str) -> ZoneInfo:
    
    rsp = await bus.call(
        Message(
            destination='org.fedoraproject.FirewallD1',
            path='/org/fedoraproject/FirewallD1',
            interface='org.fedoraproject.FirewallD1.zone',
            member='getZoneSettings2',
            signature='s',
            body=[zoneName]
        )
    )
    
    
    zoneInfo = ZoneInfo() 
    zoneInfo.Name = zoneName 
    zoneInfo.Description = rsp.body[0].get('description', Variant('s', 'description not available')).value
    zoneInfo.Interfaces = rsp.body[0].get('interfaces', Variant('as', [])).value
    zoneInfo.Services = rsp.body[0].get('services', Variant('as', [])).value
    zoneInfo.Short = rsp.body[0].get('short', Variant('s', 'short not available')).value
    zoneInfo.Sources = rsp.body[0].get('sources', Variant('as', [])).value
    
    return zoneInfo

zoneDescriptionMap = {
    None: "No description available",
    "external":"For use on external networks. You do not trust the other computers on networks to not harm your computer. Only selected incoming connections are accepted.",
    "dmz":"For computers in your demilitarized zone that are publicly-accessible with limited access to your internal network. Only selected incoming connections are accepted.",
    "work":"For use in work areas. You mostly trust the other computers on networks to not harm your computer. Only selected incoming connections are accepted.",
    "home":"For use in home areas. You mostly trust the other computers on networks to not harm your computer. Only selected incoming connections are accepted.",
    "internal":"For use on internal networks. You mostly trust the other computers on the networks to not harm your computer. Only selected incoming connections are accepted.",
}


async def GetServiceSettings2(bus: MessageBus, name: str)-> ServiceSetting:
    
    
    serviceSettings = ServiceSetting()
    
    rsp = await bus.call(
        Message(
            destination='org.fedoraproject.FirewallD1',
            path='/org/fedoraproject/FirewallD1',
            interface='org.fedoraproject.FirewallD1',
            member='getServiceSettings2',
            signature='s',
            body=[name]
        )
    )
    
    serviceSettings.Name = rsp.body[0].get('short', Variant('s', 'name not available')).value
    serviceSettings.Ports.extend(rsp.body[0].get('ports', Variant('a(ss)', [['port not available', 'protocol not available']])).value)
    serviceSettings.Description = rsp.body[0].get('description', Variant('s', 'Description not available')).value
    serviceSettings.Includes = rsp.body[0].get('includes', Variant('b', False)).value
    
    
    return serviceSettings



async def GetAvailableInterfaces(bus: MessageBus):
    
    nm_interfaces = await GetInterfaces(bus)
    used_interfaces = []
    az = await GetActiveZones(bus)
    for z in az:    
        zi = await GetZoneInfo(bus, z)
        used_interfaces.extend(zi.Interfaces)
                
    for i in nm_interfaces:
        if i in used_interfaces:
            nm_interfaces.remove(i)

    return nm_interfaces
    
    
    
    
async def AddNewZone(bus: MessageBus, zone :str, interfaces :list[str], services :list[str], addresses :str):
    
    
    props = {
        "interfaces": interfaces,
        "services": services,
        "source": addresses,
        
    }
    
    rsp = await bus.call(
    Message(
        destination='org.fedoraproject.FirewallD1',
        path='/org/fedoraproject/FirewallD1',
        interface='org.fedoraproject.FirewallD1',
        member='addZone2',
        signature='sa{sv}',
        body=[zone, props]
        )
    )
    
    return rsp.body[0]
    
    
    
    

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





def getZoneInfo(name :str, zone :dict) -> dict:

    interfaces = formatListToString(zone.get('interfaces', []))
    sources = formatListToString(zone.get('sources', []))

    return {'name':name, 'interfaces':interfaces, 'sources':sources}


async def getServicesInfo(bus: MessageBus):
    '''all not just runtime'''

    rsp = await bus.call(
        Message(
            destination='org.fedoraproject.FirewallD1',
            path='/org/fedoraproject/FirewallD1/config',
            interface='org.fedoraproject.FirewallD1.config',
            member='getServiceNames',
            signature='',
            body=[]
        )
    )
    
    services = {}
    for name in rsp.body[0]:
        serviceSetting = await GetServiceSettings2(bus, name)               
        if serviceSetting.Includes:
            for i in serviceSetting.Includes:
                subServiceSettings = await GetServiceSettings2(bus, i)
                serviceSetting.Ports.extend(subServiceSettings.Ports)
        services[name] = serviceSetting
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