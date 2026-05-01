#!/usr/bin/env python3

import asyncio

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType

from ns2.api.snmp_interface import SnmpInterface
from ns2.api.pam_interface import PamInterface
from ns2.api.accounts_interface import AccountsInterface


async def dbus_service():

    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    snmpInterface = SnmpInterface("com.novus.ns.snmp", bus)
    bus.export("/com/novus/ns", snmpInterface)

    pamInterface = PamInterface("com.novus.ns.pam")
    bus.export("/com/novus/ns", pamInterface)

    accountsInterface = AccountsInterface("com.novus.ns.accounts", bus)
    bus.export("/com/novus/ns", accountsInterface)

    # userInterface = Superuser('com.novus.ns.super')
    # bus.export('/com/novus/ns', userInterface)

    # firewallInterface = FirewalldInterface('com.novus.ns.firewall')
    # bus.export('/com/novus/ns', firewallInterface)

    # socketInterface = SocketInterface('com.novus.ns.socket')
    # bus.export('/com/novus/ns', socketInterface)

    print("Starting ns service... com.novus.ns")

    await bus.request_name("com.novus.ns")
    await asyncio.Event().wait()

    bus.disconnect()


def init_dbus_service():
    asyncio.run(dbus_service())
