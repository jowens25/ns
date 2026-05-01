import pam
from dbus_next.service import ServiceInterface, method

from dbus_next.aio import MessageBus
from dbus_next.aio.proxy_object import ProxyInterface


class PamInterface(ServiceInterface):
    def __init__(self, name):
        super().__init__(name)

    @method()
    def Authenticate(self, username: "s", password: "s") -> "b":
        p = pam.pam()
        if p.authenticate(username, password, print_failure_messages=True):
            print("authentication successful")
            return True
        else:
            print("authentication failed")

            return False


async def GetPamInterface(bus: MessageBus) -> ProxyInterface:
    introspection = await bus.introspect("com.novus.ns", "/com/novus/ns")
    obj = bus.get_proxy_object("com.novus.ns", "/com/novus/ns", introspection)
    return obj.get_interface("com.novus.ns.pam")
