from ns2.lib.nm import *
from ns2.lib.networking import *
import asyncio
from dbus_next.signature import Variant
from dbus_next.aio.proxy_object import ProxyInterface
from dbus_next.aio import MessageBus

from dbus_next import BusType
from pprint import pprint


async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    # print(await GetDevices(bus))

    dev_path = await GetDeviceByIpIface(bus, "wlp1s0")

    pprint(await GetAllDeviceProperties(bus, dev_path))


asyncio.run(main())
