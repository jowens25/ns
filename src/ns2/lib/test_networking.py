import json

from ns2.api.dbus import get_dbus
from ns2.lib.networking import GetInterfaces, GetDeviceFromInterface, set_refresh_rate


import asyncio
import requests


async def net_test():

    bus = await get_dbus()

    i = await GetInterfaces(bus)

    device = await GetDeviceFromInterface(bus, i[0])

    print(device.Path)

    rsp = await set_refresh_rate(bus, device.Path, 30)

    print(rsp.body)


import asyncio
from websockets.asyncio.client import connect
from websockets import ClientConnection


class Bridge:
    def __init__(self):
        self.conn = None

    async def connect(self):
        self.conn = await connect("ws://localhost:3000/bridge")

    async def disconnect(self):
        if self.conn:
            await self.conn.close()

    async def send(self, msg: dict):
        await self.conn.send(json.dumps(msg))
        # return json.loads(await self.conn.recv())

    async def on_message(self, msg):
        print("process message")
        print(msg)

    async def receive(self):
        async for msg in self.conn:
            await self.on_message(json.loads(msg))


# i think we are going to just make different types of json packets do what we need:
#
# {"dbus":dbuscall}
# {"cmd":commandcall}
# {"systemd":systemdcall}
from dbus_next import Message
from dbus_next.constants import BusType
from dbus_next.aio import MessageBus


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
    return rsp.body[0]


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
    return rsp.body[0]


async def tryBridge():

    await CallMakeBridge("admin")

    await asyncio.sleep(1)

    bridge = Bridge()
    await bridge.connect()

    asyncio.create_task(bridge.receive())

    print(await bridge.send({"test1": "hi", "test2": "hi"}))
    print(await bridge.send({"test1": "hi", "test2": "hi"}))
    print(await bridge.send({"test1": "hi", "test2": "hi"}))
    print(await bridge.send({"test1": "hi", "test2": "hi"}))
    print(await bridge.send({"test1": "hi", "test2": "hi"}))

    await asyncio.sleep(2)

    await bridge.disconnect()

    await CallCloseBridge()


def run_test():

    asyncio.run(tryBridge())

    # print(
    #    bridgeCall(
    #        "com.novus.ns",
    #        "/com/novus/ns",
    #        "com.novus.ns.pam",
    #        "GetStuff",
    #        [],
    #    )
    # )
    #
    # print(
    #    bridgeCall(
    #        "com.novus.ns",
    #        "/com/novus/ns",
    #        "com.novus.ns.pam",
    #        "Authenticate",
    #        ["jowens", "jowens"],
    #    )
    # )
    #
    #    devices = bridgeCall(
    #        destination="org.freedesktop.NetworkManager",
    #        path="/org/freedesktop/NetworkManager",
    #        method="org.freedesktop.NetworkManager.GetDevices",
    #        args=[],
    #    )
    #
    #    print(devices)
    #
    #    print(
    #        "state: ",
    #        bridgeCall(
    #            destination="org.freedesktop.NetworkManager",
    #            path="/org/freedesktop/NetworkManager",
    #            method="org.freedesktop.DBus.Properties.Get",
    #            args=["org.freedesktop.NetworkManager", "State"],
    #        ),
    #    )
    #
    #    prop = bridgeCall(
    #        destination="org.freedesktop.NetworkManager",
    #        path=devices[1],
    #        method="org.freedesktop.DBus.Properties.Get",
    #        args=["org.freedesktop.NetworkManager.Device", "ActiveConnection"],
    #    )
    #
    #    print(prop)

    # bridgeCall(
    #    # Message(
    #    destination="org.freedesktop.NetworkManager",
    #    path=devices[1],
    #    iface="org.freedesktop.NetworkManager.Device.Statistics",
    #    method="Get",
    #    # signature="ssv",
    #    args=[],
    #    # )
    # )

    # print(
    #    "allowed? result:",
    #    bridgeCall(
    #        destination="com.novus.ns",
    #        path="/com/novus/ns",
    #        method="com.novus.ns.pam.GetStuff",
    #        args=[],
    #    ),
    # )
