from dbus_next.aio import MessageBus
from dbus_next import Message
import asyncio
from ns2.lib.dbus import GetBridgePid


async def test_tcp():

    bus = MessageBus(bus_address="tcp:host=localhost,port=3000")
    await bus.connect()

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
    print(rsp.body[0])

    rsp = await bus.call(
        Message(
            destination="org.freedesktop.NetworkManager",
            path="/org/freedesktop/NetworkManager",
            interface="org.freedesktop.NetworkManager",
            member="GetDevices",
            signature="",
            body=[],
        )
    )
    print(rsp.body[0])

    rsp = await bus.call(
        Message(
            destination="org.freedesktop.DBus",
            path="/org/freedesktop/DBus",
            interface="org.freedesktop.DBus",
            member="GetConnectionCredentials",
            signature="s",
            body=[bus.unique_name],
        )
    )
    print(rsp.body[0].get("UnixUserID").value)

    rsp = await bus.call(
        Message(
            destination="com.novus.ns",
            path="/com/novus/ns",
            interface="com.novus.ns.snmp",
            member="Reset",
            signature="",
            body=[],
        )
    )
    print(rsp.body[0])


if __name__ == "__main__":

    asyncio.run(test_tcp())
