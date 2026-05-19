from dbus_next.aio import MessageBus
from dbus_next import Message
from dbus_next.constants import BusType

### DBUS CALLS FOR BRIDGE


async def CallPamAuthenticate(username, password) -> bool:

    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    rsp = await bus.call(
        Message(
            destination="com.novus.ns",
            path="/com/novus/ns",
            interface="com.novus.ns.pam",
            member="Authenticate",
            signature="ss",
            body=[username, password],
        )
    )
    bus.disconnect()
    return rsp.body[0]


async def GetBridgePid():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    rsp = await bus.call(
        Message(
            destination="com.novus.ns",
            path="/com/novus/ns",
            interface="org.freedesktop.DBus.Properties",
            member="Get",
            signature="ss",
            body=["com.novus.ns.bridge", "pid"],
        )
    )
    bus.disconnect()
    return rsp.body[0].value


async def CallCloseBridge():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    rsp = await bus.call(
        Message(
            destination="com.novus.ns",
            path="/com/novus/ns",
            interface="com.novus.ns.bridge",
            member="Close",
            signature="",
            body=[],
        )
    )
    bus.disconnect()
    return rsp.body[0]


async def CallMakeBridge(username: str) -> int:
    """returns pid of bridge"""
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    rsp = await bus.call(
        Message(
            destination="com.novus.ns",
            path="/com/novus/ns",
            interface="com.novus.ns.bridge",
            member="Make",
            signature="s",
            body=[username],
        )
    )
    bus.disconnect()
    return int(rsp.body[0])
