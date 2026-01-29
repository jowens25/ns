from dbus_next.aio import MessageBus
from dbus_next import BusType
import asyncio


class NM:
    def __init__(self):
        self.bus = None
        self.introspection =  None
        self.object =  None
        self.interface = None
        self.properties_interface = None # implements
        self.properties = None


    async def connect(self):
        loop = asyncio.get_running_loop()
        self.bus = MessageBus(bus_type=BusType.SYSTEM)
        self.bus._loop = loop
        self.bus = await self.bus.connect()

    async def setup(self):
        self.introspection = await self.bus.introspect('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')
        self.object = self.bus.get_proxy_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager', self.introspection)
        self.interface = self.object.get_interface('org.freedesktop.NetworkManager')
        self.properties_interface = self.object.get_interface('org.freedesktop.DBus.Properties')
        self.properties = await self.properties_interface.call_get_all('org.freedesktop.NetworkManager')


    async def reload(self):
        self.object.call_reload('org.freedesktop.NetworkManager')


    def disconnect(self):
        self.bus.disconnect()

    