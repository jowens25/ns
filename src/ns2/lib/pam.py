import dbus_next
from dbus_next.message_bus import MessageBus


async def GetPamInterface(bus: MessageBus):
    introspection = await bus.introspect("com.novus.ns", "/com/novus/ns")
    obj = bus.get_proxy_object("com.novus.ns", "/com/novus/ns", introspection)
    return obj.get_interface("com.novus.ns.snmp")
