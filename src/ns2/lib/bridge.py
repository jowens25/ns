import asyncio


from dbus_next import Message
from dbus_next.constants import BusType
from dbus_next.aio import MessageBus

# app bus is a dbus connection over tcp via localhost:3000 called a bridge
BRIDGE: MessageBus = None


async def SetupBridge(_username: str) -> str:
    """on new user session create new bridge, cancel old one?, returns connected instance"""
    # 1. get ref, clean it up
    # 2. new ref, build it for user
    # 3. connect, check connection
    # 4. if its good return name, else false...?
    currentBridge = GetBridge()
    if currentBridge is not None:
        await CleanupBridge()

    await CallMakeBridge(_username)
    await asyncio.sleep(0.5)
    bus = MessageBus(bus_address="tcp:host=localhost,port=3000")
    await bus.connect()

    if bus.connected:
        print("new bridge connected")
        SetBridge(bus)
        return await GetActiveUser()
    else:
        return False


async def CleanupBridge():
    global BRIDGE
    BRIDGE.disconnect()
    await BRIDGE.wait_for_disconnect()
    await CallCloseBridge()
    BRIDGE = None


def GetBridge() -> MessageBus:
    global BRIDGE
    return BRIDGE


def SetBridge(bus: MessageBus):
    global BRIDGE
    BRIDGE = bus


async def GetActiveUser() -> str:

    rsp = await BridgeCall(
        destination="com.novus.ns",
        path="/com/novus/ns",
        interface="com.novus.ns.bridge",
        member="GetActiveUser",
        signature="",
        body=[],
    )

    return rsp.body[0]


async def CheckBridge(username: str) -> bool:
    """Checks if user matches bridge"""
    return username == await GetActiveUser()


async def BridgeCall(
    destination: str, path: str, interface: str, member: str, signature: str, body
) -> Message:
    """Connect to proxy bus, make call return response"""
    b = GetBridge()
    rsp = await b.call(
        Message(
            destination=destination,
            path=path,
            interface=interface,
            member=member,
            signature=signature,
            body=body,
        )
    )

    return rsp


async def BusCall(
    destination: str, path: str, interface: str, member: str, signature: str, body
) -> Message:
    """Connect to system bus, no proxy, make a call, return reponse, disconnect"""
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    rsp = await bus.call(
        Message(
            destination=destination,
            path=path,
            interface=interface,
            member=member,
            signature=signature,
            body=body,
        )
    )
    bus.disconnect()
    return rsp


async def CallPamAuthenticate(username, password) -> bool:

    rsp = await BusCall(
        destination="com.novus.ns",
        path="/com/novus/ns",
        interface="com.novus.ns.pam",
        member="Authenticate",
        signature="ss",
        body=[username, password],
    )

    return rsp.body[0]


async def GetBridgePid():
    rsp = await BusCall(
        destination="com.novus.ns",
        path="/com/novus/ns",
        interface="org.freedesktop.DBus.Properties",
        member="Get",
        signature="ss",
        body=["com.novus.ns.bridge", "pid"],
    )

    return rsp.body[0].value


async def CallCloseBridge():
    rsp = await BusCall(
        destination="com.novus.ns",
        path="/com/novus/ns",
        interface="com.novus.ns.bridge",
        member="Close",
        signature="",
        body=[],
    )

    return rsp.body[0]


async def CallMakeBridge(username: str) -> int:
    """returns pid of bridge"""

    rsp = await BusCall(
        destination="com.novus.ns",
        path="/com/novus/ns",
        interface="com.novus.ns.bridge",
        member="Make",
        signature="s",
        body=[username],
    )

    return int(rsp.body[0])
