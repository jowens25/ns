import json
from pprint import pprint
import uuid

from ns2.api.dbus import get_dbus
from ns2.lib.networking import GetInterfaces, GetDeviceFromInterface, set_refresh_rate

import asyncio
from ns2.lib.bridge import SetBridge

from numpy import uint
from ns2.lib.systemd1 import SystemdRestart


async def net_test():

    bus = await get_dbus()

    i = await GetInterfaces(bus)

    device = await GetDeviceFromInterface(bus, i[0])

    print(device.Path)

    rsp = await set_refresh_rate(bus, device.Path, 30)

    print(rsp.body)


from ns2.lib.bridge import DbusCall, CallMakeBridge, Bridge, CallCloseBridge
from ns2.lib.networking import *


async def TestFunc():
    print("running test?")

    await CallMakeBridge("admin")
    await asyncio.sleep(1)

    bridge = Bridge()
    await bridge.connect()

    SetBridge(bridge)

    device_path = await GetDeviceByIpIface("enp3s0")

    ip4_config_path = await GetNmProp(device_path, "Device", "Ip4Config")
    ip4AddressData = await GetNmProp(
        ip4_config_path, "IP4Config", "AddressData", "aa{sv}"
    )

    print(ip4AddressData)

    # rsp = await GetAppliedConnection(device_path, 0)
    #
    # print(rsp)

    # print(await GetInterfaceData("enp3s0"))
    # rsp = await SystemdRestart("snmpd.service")

    # print(rsp)

    await bridge.cleanup()

    # devices = await DbusCall(
    #    bridge,
    #    destination="org.freedesktop.NetworkManager",
    #    path="/org/freedesktop/NetworkManager",
    #    method="org.freedesktop.NetworkManager.GetDevices",
    #    args=[],
    #    signature=None,
    # )
    # pprint(devices)
    #
    # print(devices[1])
    #
    # pprint(
    #    await DbusCall(
    #        bridge,
    #        destination="org.freedesktop.NetworkManager",
    #        path="/org/freedesktop/NetworkManager/Devices/2",
    #        method="org.freedesktop.NetworkManager.Device.GetAppliedConnection",
    #        args=["0"],
    #        signature=["u"],
    #    ),
    # )

    # pprint(
    #    await DbusCall(
    #        bridge,
    #        destination="org.freedesktop.NetworkManager",
    #        path="/org/freedesktop/NetworkManager",
    #        method="org.freedesktop.NetworkManager.Enable",
    #        args=[False],
    #        # signature=["b"],
    #    ),
    # )


#
# prop = await DbusCall(
#    bridge,
#    destination="org.freedesktop.NetworkManager",
#    path=devices[1],
#    method="org.freedesktop.DBus.Properties.Get",
#    args=["org.freedesktop.NetworkManager.Device", "ActiveConnection"],
# )
#
# print(prop)

# await bridge.disconnect()
# await CallCloseBridge()


if __name__ == "__main__":

    asyncio.run(TestFunc())


#


# print("no test run")
# CheckBridge
# asyncio.run(CheckBridge())

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
