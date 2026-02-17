from systemd import systemd_start, systemd_restart, systemd_stop, isActive
import asyncio
from dbus_next.signature import Variant
from dbus_next.aio.proxy_object import ProxyInterface
from dbus_next.aio import MessageBus

from dbus_next import BusType




async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    print(await systemd_stop(bus, 'snmpd.service'))
    
    print(await isActive(bus, "snmpd.service"))

asyncio.run(main())