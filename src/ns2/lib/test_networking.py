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


def run_test():

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

    print(
        "allowed? result:",
        bridgeCall(
            destination="com.novus.ns",
            path="/com/novus/ns",
            method="com.novus.ns.pam.GetStuff",
            args=[],
        ),
    )
