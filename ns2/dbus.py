from dbus_next import BusType
from dbus_next.aio import MessageBus
from nicegui import app

AppBus: MessageBus = None

async def setup_dbus():
    global AppBus
    if AppBus is None:
        AppBus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    return AppBus

async def cleanup_dbus():
    global AppBus
    if AppBus is not None:
        AppBus.disconnect()
        AppBus = None

async def get_dbus():
    if AppBus is None:
        return await setup_dbus()
    else:
        return AppBus