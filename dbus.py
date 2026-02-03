from dbus_next import BusType
from dbus_next.aio import MessageBus

global AppBus

async def setup():
    global AppBus
    AppBus = await MessageBus(bus_type=BusType.SYSTEM).connect()

async def cleanup():
    global AppBus
    AppBus.disconnect()

