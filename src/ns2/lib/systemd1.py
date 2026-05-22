import asyncio
from dbus_next.signature import Variant
from dbus_next.aio.proxy_object import ProxyInterface
from dbus_next.aio import MessageBus as MessageBus
from dbus_next.glib import MessageBus as SyncBus
from dbus_next import Message, MessageType

from ns2.lib.bridge import DbusCall, WriteBridge


async def ListUnits() -> str:

    rsp = await DbusCall(
        destination="org.freedesktop.systemd1",
        path="/org/freedesktop/systemd1",
        interface="org.freedesktop.systemd1.Manager",
        member="ListUnits",
        signature="",
        body=[],
    )

    return rsp


# async def GetUnitPath(service: str) -> str:
#     rsp = await DbusCall(
#         destination="org.freedesktop.systemd1",
#         path="/org/freedesktop/systemd1",
#         interface="org.freedesktop.systemd1.Manager",
#         member="GetUnit",
#         signature="s",
#         body=[service],
#     )

#     return rsp


# async def GetUnitProperties(unitPath: str) -> dict:

#     rsp = await DbusCall(
#         destination="org.freedesktop.systemd1",
#         path=unitPath,
#         interface="org.freedesktop.DBus.Properties",
#         member="GetAll",
#         signature="s",
#         body=["org.freedesktop.systemd1.Unit"],
#     )
#     return rsp


async def GetServiceState(service: str) -> str:
    status = await WriteBridge({"systemd": "status", "service": service})
    return status.get("status", "inactive")


async def isActive(service: str) -> bool:

    state = await GetServiceState(service)
    print(f"{service} is active: {state}")

    if state == "active":
        return True
    else:
        return False


async def SystemdStop(service: str) -> dict:
    return await WriteBridge({"systemd": "stop", "service": service})


async def SystemdStart(service: str) -> dict:
    return await WriteBridge({"systemd": "start", "service": service})


async def SystemdRestart(service: str) -> dict:
    return await WriteBridge({"systemd": "restart", "service": service})
