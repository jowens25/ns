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




async def AddSource(bus: MessageBus, zoneName: str, source:str):
    rsp = await bus.call(
        Message(
             destination='org.fedoraproject.FirewallD1',
            path='/org/fedoraproject/FirewallD1',
            interface='org.fedoraproject.FirewallD1.zone',
            member='addSource',
            signature='ss',
            body=[zoneName, source]
        )
    )
    return rsp.body[0]

async def RemoveSource(bus: MessageBus, zoneName: str, source:str):
    rsp = await bus.call(
        Message(
             destination='org.fedoraproject.FirewallD1',
            path='/org/fedoraproject/FirewallD1',
            interface='org.fedoraproject.FirewallD1.zone',
            member='removeSource',
            signature='ss',
            body=[zoneName, source]
        )
    )
    return rsp.body[0]

async def AddInterface(bus: MessageBus, zoneName: str, interfaceName:str):
    rsp = await bus.call(
        Message(
             destination='org.fedoraproject.FirewallD1',
            path='/org/fedoraproject/FirewallD1',
            interface='org.fedoraproject.FirewallD1.zone',
            member='addInterface',
            signature='ss',
            body=[zoneName, interfaceName]
        )
    )
    return rsp.body[0]

async def RemoveInterface(bus: MessageBus, zoneName: str, interfaceName:str):
    rsp = await bus.call(
        Message(
             destination='org.fedoraproject.FirewallD1',
            path='/org/fedoraproject/FirewallD1',
            interface='org.fedoraproject.FirewallD1.zone',
            member='removeInterface',
            signature='ss',
            body=[zoneName, interfaceName]
        )
    )
    return rsp.body[0]


async def ListZones(bus: MessageBus):
    rsp = await bus.call(
        Message(
            destination='org.fedoraproject.FirewallD1',
            path='/org/fedoraproject/FirewallD1/config',
            interface='org.fedoraproject.FirewallD1.config',
            member='listZones',
            signature='',
            body=[]
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

async def GetAllZones(bus: MessageBus):
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
    
    activeZones = rsp.body[0]


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
    
    runtimeZones = rsp.body[0]


    peranentZones = rsp.body[0]

    #print(peranentZones)




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

def MakeZoneInfo(settings: dict):
    zoneInfo = ZoneInfo() 
    zoneInfo.Description = settings.get('description', Variant('s', 'description not available')).value
    zoneInfo.Interfaces = settings.get('interfaces', Variant('as', [])).value
    zoneInfo.Services = settings.get('services', Variant('as', [])).value
    zoneInfo.Short = settings.get('short', Variant('s', 'short not available')).value
    zoneInfo.Sources = settings.get('sources', Variant('as', [])).value
    
    return zoneInfo

async def GetSettings2(bus: MessageBus, zonePath: str) -> ZoneInfo:
    '''permanent settings of zone (path)'''
    rsp = await bus.call(
        Message(
            destination='org.fedoraproject.FirewallD1',
            path=zonePath,
            interface='org.fedoraproject.FirewallD1.config.zone',
            member='getSettings2',
            signature='',
            body=[]
        )
    )
    
    return rsp.body[0]

async def GetZoneSettings2(bus: MessageBus, zoneName: str) -> ZoneInfo:
    '''runtime settings of zone'''
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
    
    return rsp.body[0]

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
        zi = MakeZoneInfo(await GetZoneSettings2(bus, z))
        used_interfaces.extend(zi.Interfaces)
                
    for i in nm_interfaces:
        if i in used_interfaces:
            nm_interfaces.remove(i)

    return nm_interfaces
    
    
    
    
    

    

    
    
    

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


async def GetFirewalldZone(bus: MessageBus):
    file_name = 'org.fedoraproject.FirewallD1.zone.xml'
    introspection = await bus.introspect('org.fedoraproject.FirewallD1', '/org/fedoraproject/FirewallD1')
    #pprint(introspection.tostring())
    obj = bus.get_proxy_object('org.fedoraproject.FirewallD1', '/org/fedoraproject/FirewallD1', introspection)
    return obj.get_interface('org.fedoraproject.FirewallD1.zone')



async def GetZoneByName(bus: MessageBus, name):
    '''get zone path from perm conf'''
    rsp = await bus.call(
        Message(
            destination='org.fedoraproject.FirewallD1',
            path='/org/fedoraproject/FirewallD1/config',
            interface='org.fedoraproject.FirewallD1.config',
            member='getZoneByName',
            signature='s',
            body=[name],
        )
    )
    
    return rsp.body[0]




async def Update2(bus: MessageBus, zonePath: str, settings: dict):

    rsp = await bus.call(
    Message(
        destination='org.fedoraproject.FirewallD1',
        path=zonePath,
        interface='org.fedoraproject.FirewallD1.config.zone',
        member='update2',
        signature='a{sv}',
        body=[settings]
        )
    )
    
    #return rsp.body[0]


def getZoneInfo(name :str, zone :dict) -> dict:

    interfaces = formatListToString(zone.get('interfaces', []))
    sources = formatListToString(zone.get('sources', []))

    return {'name':name, 'interfaces':interfaces, 'sources':sources}





async def AddZone(bus: MessageBus, zoneName: str, interfaces: list[str], sources: list[str]):
    zp = await GetZoneByName(bus, zoneName)
    
    for interface in interfaces:
        print(await AddInterface(bus, zoneName, interface))
    
    for source in sources:
        print(await AddSource(bus, zoneName, source))
        
    settings = {
        'interfaces': Variant('as', interfaces),
        'sources': Variant('as', sources)
    }
    
    print(f'add zone settings: {settings}')
    
    await Update2(bus, zp, settings)
            
async def RemoveZone(bus: MessageBus, zoneName: str):
    
    print("trying to remove:: ", zoneName)
    zp = await GetZoneByName(bus, zoneName)
    
    settings = await GetZoneSettings2(bus, zoneName)
    
    print(f'get zone settings: {settings}')
    
    print()
    
    zoneInfo = MakeZoneInfo(settings)
    
    print(zoneInfo)
    print()

    print(f'get settings 2: {await GetSettings2(bus, zp)}')
    print()

    #zoneInfo = MakeZoneInfo(settings)
    #
    #print(zoneInfo)
    #
    for interface in zoneInfo.Interfaces:
        print(await RemoveInterface(bus, zoneName, interface))
    #
    #for source in zoneInfo.Sources:
    #    print(await RemoveSource(bus, zoneName, source))
    
    #print(settings)
    del settings['interfaces']
    #settings = settings.pop('sources')    
#
    await Update2(bus, zp, settings)
    

            

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



    
    