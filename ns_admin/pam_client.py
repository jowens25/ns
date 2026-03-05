from dbus_next.aio import MessageBus

import asyncio

loop = asyncio.get_event_loop()
from dbus_next.constants import BusType

async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    # the introspection xml would normally be included in your project, but
    # this is convenient for development
    introspection = await bus.introspect('com.novus.ns', '/com/novus/ns')

    obj = bus.get_proxy_object('com.novus.ns', '/com/novus/ns', introspection)
    interface = obj.get_interface('com.novus.ns.pam')
    #properties = obj.get_interface('org.freedesktop.DBus.Properties')

    user = input("username?: ")
    password = input("password?: ")
    ## call methods on the interface (this causes the media player to play)
    resp = await interface.call_authenticate(user, password)
    print(resp)
    #volume = await player.get_volume()
    #print(f'current volume: {volume}, setting to 0.5')
#
    #await player.set_volume(0.5)
#
    ## listen to signals
    #def on_properties_changed(interface_name, changed_properties, invalidated_properties):
    #    for changed, variant in changed_properties.items():
    #        print(f'property changed: {changed} - {variant.value}')
#
    #properties.on_properties_changed(on_properties_changed)

    await loop.create_future()

loop.run_until_complete(main())