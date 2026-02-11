from systemd import systemd_start
import asyncio
from dbus_next.signature import Variant
from dbus_next.aio.proxy_object import ProxyInterface
from dbus_next.aio import MessageBus
from dbus_next.glib import MessageBus as SyncBus

from dbus_next import BusType




async def main():
    bus = SyncBus(bus_type=BusType.SYSTEM).connect_sync()

    print(await systemd_start(bus, 'snmpd.service'))
    
    print("started")

asyncio.run(main())