import asyncio

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType

from snmp_interface import SnmpInterface
from pam_interface import PamInterface
from systemd_lib import *

from cockpit_dbus_superuser_service import Superuser
async def main():
    
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    
    snmpInterface = SnmpInterface('com.novus.ns.snmp')
    bus.export('/com/novus/ns', snmpInterface)
    snmpInterface.bus = bus

    pamInterface = PamInterface('com.novus.ns.pam')
    bus.export('/com/novus/ns', pamInterface)
    
    userInterface = Superuser('com.novus.ns.super')
    bus.export('/com/novus/ns', userInterface)
    
    #firewallInterface = FirewalldInterface('com.novus.ns.firewall')
    #bus.export('/com/novus/ns', firewallInterface)

    #socketInterface = SocketInterface('com.novus.ns.socket')
    #bus.export('/com/novus/ns', socketInterface)

    print("Starting ns service... com.novus.ns")
    
    await bus.request_name('com.novus.ns')
    await asyncio.Event().wait()

    bus.disconnect()

asyncio.run(main())
