from dataclasses import field

from typing import Optional
from nicegui import binding

from ns2.lib.networking import GetInterfaces

from ns2.common import formatListToString

from dbus_next.signature import Variant
from ns2.utils import log


from ns2.lib.bridge import BridgeCall


@binding.bindable_dataclass
class ServiceSetting:
    Version: Optional[str] = ""
    Name: Optional[str] = ""
    Description: Optional[str] = ""
    Ports: Optional[list[str]] = field(default_factory=list)
    ModuleNames: Optional[list[str]] = field(default_factory=list)
    Destinations: Optional[dict] = field(default_factory=dict)
    Protocols: Optional[list[str]] = field(default_factory=list)
    SourcePorts: Optional[list[str]] = field(default_factory=list)
    Includes: Optional[list[str]] = field(default_factory=list)
    Helpers: Optional[list[str]] = field(default_factory=list)


@binding.bindable_dataclass
class ZoneInfo:
    Description: Optional[str] = ""
    Interfaces: Optional[list[str]] = field(default_factory=list)
    Services: Optional[list[str]] = field(default_factory=list)
    Short: Optional[str] = ""
    Name: Optional[str] = ""
    ServiceSettings: Optional[dict[ServiceSetting]] = field(default_factory=dict)
    Sources: Optional[list[str]] = field(default_factory=list)


@binding.bindable_dataclass
class FirewallInfo:
    Enable: Optional[bool] = False
    Status: Optional[str] = ""
    ActiveZones: Optional[dict[dict]] = field(default_factory=dict)
    AllowedAddresses: Optional[list[str]] = field(default_factory=list)
    Services: Optional[dict[dict]] = field(default_factory=dict)
    ZoneInfos: Optional[dict[ZoneInfo]] = field(default_factory=dict)


async def zoneRemoveService(zoneName: str, serviceName: str):

    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path="/org/fedoraproject/FirewallD1",
        interface="org.fedoraproject.FirewallD1.zone",
        member="removeService",
        signature="ss",
        body=[zoneName, serviceName],
    )
    return rsp.body[0]


async def zoneAddService(zoneName: str, serviceName: str):

    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path="/org/fedoraproject/FirewallD1",
        interface="org.fedoraproject.FirewallD1.zone",
        member="addService",
        signature="ss",
        body=[zoneName, serviceName, 0],
    )
    return rsp.body[0]


async def zoneConfigRemoveService(zonePath: str, serviceName: str):
    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path=zonePath,
        interface="org.fedoraproject.FirewallD1.config.zone",
        member="removeService",
        signature="s",
        body=[serviceName],
    )
    return rsp.body[0]


async def zoneConfigAddService(zonePath: str, serviceName: str):
    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path=zonePath,
        interface="org.fedoraproject.FirewallD1.config.zone",
        member="addService",
        signature="s",
        body=[serviceName],
    )
    return rsp.body[0]


async def AddSource(zoneName: str, source: str):
    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path="/org/fedoraproject/FirewallD1",
        interface="org.fedoraproject.FirewallD1.zone",
        member="addSource",
        signature="ss",
        body=[zoneName, source],
    )
    return rsp.body[0]


async def RemoveSource(zoneName: str, source: str):
    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path="/org/fedoraproject/FirewallD1",
        interface="org.fedoraproject.FirewallD1.zone",
        member="removeSource",
        signature="ss",
        body=[zoneName, source],
    )
    return rsp.body[0]


async def AddInterface(zoneName: str, interfaceName: str):
    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path="/org/fedoraproject/FirewallD1",
        interface="org.fedoraproject.FirewallD1.zone",
        member="addInterface",
        signature="ss",
        body=[zoneName, interfaceName],
    )
    return rsp.body[0]


async def RemoveInterface(zoneName: str, interfaceName: str):
    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path="/org/fedoraproject/FirewallD1",
        interface="org.fedoraproject.FirewallD1.zone",
        member="removeInterface",
        signature="ss",
        body=[zoneName, interfaceName],
    )
    return rsp.body[0]


async def ListZones():
    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path="/org/fedoraproject/FirewallD1/config",
        interface="org.fedoraproject.FirewallD1.config",
        member="listZones",
        signature="",
        body=[],
    )

    return rsp.body[0]


async def GetActiveZones() -> list[ZoneInfo]:

    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path="/org/fedoraproject/FirewallD1",
        interface="org.fedoraproject.FirewallD1.zone",
        member="getActiveZones",
        signature="",
        body=[],
    )

    return rsp.body[0]


async def GetZones() -> list[ZoneInfo]:
    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path="/org/fedoraproject/FirewallD1",
        interface="org.fedoraproject.FirewallD1.zone",
        member="getZones",
        signature="",
        body=[],
    )
    return rsp.body[0]


# Sorted from least to most trusted
#
# external
# dmz
# work
# home
# internal


async def GetSelectableZones():
    default_zones = ["public", "external", "dmz", "work", "home", "internal"]
    available_zones = []
    allzones = await GetZones()
    actzones = await GetActiveZones()
    for z in allzones:
        log.info(z)
        if (z in default_zones) and (z not in actzones):
            available_zones.append(z)

    return available_zones


def MakeZoneInfo(settings: dict):
    zoneInfo = ZoneInfo()
    zoneInfo.Description = settings.get("description", "description not available")
    zoneInfo.Interfaces = settings.get("interfaces", [])
    zoneInfo.Services = settings.get("services", [])
    zoneInfo.Short = settings.get("short", "short not available")
    zoneInfo.Sources = settings.get("sources", [])

    return zoneInfo


async def GetSettings2(zonePath: str) -> ZoneInfo:
    """permanent settings of zone (path)"""
    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path=zonePath,
        interface="org.fedoraproject.FirewallD1.config.zone",
        member="getSettings2",
        signature="",
        body=[],
    )

    return rsp.body[0]


async def GetZoneSettings2(zoneName: str) -> ZoneInfo:
    """runtime settings of zone"""
    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path="/org/fedoraproject/FirewallD1",
        interface="org.fedoraproject.FirewallD1.zone",
        member="getZoneSettings2",
        signature="s",
        body=[zoneName],
    )
    return rsp.body[0]


zoneDescriptionMap = {
    None: "No description available",
    "external": "For use on external networks. You do not trust the other computers on networks to not harm your computer. Only selected incoming connections are accepted.",
    "dmz": "For computers in your demilitarized zone that are publicly-accessible with limited access to your internal network. Only selected incoming connections are accepted.",
    "work": "For use in work areas. You mostly trust the other computers on networks to not harm your computer. Only selected incoming connections are accepted.",
    "home": "For use in home areas. You mostly trust the other computers on networks to not harm your computer. Only selected incoming connections are accepted.",
    "internal": "For use on internal networks. You mostly trust the other computers on the networks to not harm your computer. Only selected incoming connections are accepted.",
}


async def GetServiceSettings2(name: str) -> ServiceSetting:

    serviceSettings = ServiceSetting()

    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path="/org/fedoraproject/FirewallD1",
        interface="org.fedoraproject.FirewallD1",
        member="getServiceSettings2",
        signature="s",
        body=[name],
    )

    serviceSettings.Name = rsp.body[0].get("short", Variant("s", "not available")).value
    serviceSettings.Ports.extend(
        rsp.body[0]
        .get(
            "ports",
            Variant("a(ss)", [["port not available", "protocol not available"]]),
        )
        .value
    )
    serviceSettings.Description = (
        rsp.body[0].get("description", Variant("s", "Description not available")).value
    )
    serviceSettings.Includes = rsp.body[0].get("includes", Variant("b", False)).value

    return serviceSettings


async def GetAvailableInterfaces():

    nm_interfaces = await GetInterfaces()
    used_interfaces = []
    az = await GetActiveZones()
    for z in az:
        zi = MakeZoneInfo(await GetZoneSettings2(z))
        used_interfaces.extend(zi.Interfaces)

    for i in nm_interfaces:
        if i in used_interfaces:
            nm_interfaces.remove(i)

    return nm_interfaces


async def GetZoneByName(name):
    """get zone path from perm conf"""
    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path="/org/fedoraproject/FirewallD1/config",
        interface="org.fedoraproject.FirewallD1.config",
        member="getZoneByName",
        signature="s",
        body=[name],
    )

    return rsp.body[0]


async def Update2(zonePath: str, settings: dict):

    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path=zonePath,
        interface="org.fedoraproject.FirewallD1.config.zone",
        member="update2",
        signature="a{sv}",
        body=[settings],
    )

    return rsp.body[0]


def getZoneInfo(name: str, zone: dict) -> dict:

    interfaces = formatListToString(zone.get("interfaces", []))
    sources = formatListToString(zone.get("sources", []))

    return {"name": name, "interfaces": interfaces, "sources": sources}


async def AddZone(zoneName: str, interfaces: list[str], sources: list[str]):
    zp = await GetZoneByName(zoneName)

    for interface in interfaces:
        log.info(await AddInterface(zoneName, interface))

    for source in sources:
        log.info(await AddSource(zoneName, source))

    settings = {
        "interfaces": Variant("as", interfaces),
        "sources": Variant("as", sources),
    }

    await Update2(zp, settings)


async def RemoveZone(zoneName: str):

    zp = await GetZoneByName(zoneName)
    settings = await GetZoneSettings2(zoneName)
    zoneInfo = MakeZoneInfo(settings)

    for interface in zoneInfo.Interfaces:
        log.info(await RemoveInterface(zoneName, interface))

    for source in zoneInfo.Sources:
        log.info(await RemoveSource(zoneName, source))

    if settings.get("interfaces") is not None:
        del settings["interfaces"]

    await Update2(zp, settings)


async def getServicesInfo():
    """all not just runtime"""

    rsp = await BridgeCall(
        destination="org.fedoraproject.FirewallD1",
        path="/org/fedoraproject/FirewallD1/config",
        interface="org.fedoraproject.FirewallD1.config",
        member="getServiceNames",
        signature="",
        body=[],
    )

    services = {}
    for name in rsp.body[0]:
        serviceSetting = await GetServiceSettings2(name)
        if serviceSetting.Includes:
            for i in serviceSetting.Includes:
                subServiceSettings = await GetServiceSettings2(i)
                serviceSetting.Ports.extend(subServiceSettings.Ports)
        services[name] = serviceSetting
    return services


def getUdpPorts(ports) -> list:
    out = []
    for p in ports:
        if p[1] == "udp":
            out.append(p[0])

    return formatListToString(out)


def getTcpPorts(ports) -> list:
    out = []
    for p in ports:
        if p[1] == "tcp":
            out.append(p[0])

    return formatListToString(out)


def formatServicesInRows(serviceSettings: dict):

    rows = []
    for n, s in serviceSettings.items():
        rows.append(
            {
                # "Select": False,
                "Service": n,
                "UDP": getUdpPorts(s.Ports),
                "TCP": getTcpPorts(s.Ports),
                "Description": s.Description,
                # ,"remove": ''
            }
        )

    # plog.info(rows)
    return rows
