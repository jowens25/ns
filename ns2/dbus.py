#!/usr/bin/env python3

import asyncio

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType

from ns2.snmp_interface import SnmpInterface
from ns2.pam_interface import PamInterface

async def dbus_service():
    
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    
    snmpInterface = SnmpInterface('com.novus.ns.snmp')
    bus.export('/com/novus/ns', snmpInterface)
    snmpInterface.bus = bus

    pamInterface = PamInterface('com.novus.ns.pam')
    bus.export('/com/novus/ns', pamInterface)
    
    #userInterface = Superuser('com.novus.ns.super')
    #bus.export('/com/novus/ns', userInterface)
    
    #firewallInterface = FirewalldInterface('com.novus.ns.firewall')
    #bus.export('/com/novus/ns', firewallInterface)

    #socketInterface = SocketInterface('com.novus.ns.socket')
    #bus.export('/com/novus/ns', socketInterface)

    print("Starting ns service... com.novus.ns")
    
    await bus.request_name('com.novus.ns')
    await asyncio.Event().wait()

    bus.disconnect()


def main():
    asyncio.run(dbus_service())
    
    
if __name__ == "__main__":
    main()




AppBus: MessageBus = None

async def setup_dbus():
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
        return await setup_dbus()
    else:
        return AppBus
    
    
    