from dbus_next import BusType
from dbus_next.aio import MessageBus
from dbus_next.glib import MessageBus as SyncBus

global AppBus
global SysBus

async def setup():
    global AppBus
    global SysBus
    AppBus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    
    SysBus = SyncBus(bus_type=BusType.SYSTEM).connect_sync()

async def cleanup():
    global AppBus
    global SysBus
    AppBus.disconnect()
    SysBus.disconnect()


