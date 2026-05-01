from dbus_next.aio import MessageBus
from dbus_next.constants import BusType

AppBus: MessageBus = None


async def connect_to_dbus():
    global AppBus
    if AppBus is None:
        AppBus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    return AppBus


def cleanup_dbus():
    global AppBus
    if AppBus is not None:
        AppBus.disconnect()
        AppBus = None


async def get_dbus():
    if AppBus is None:
        return await connect_to_dbus()
    else:
        return AppBus
