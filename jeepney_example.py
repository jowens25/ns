"""
This example simulates two clients interacting with the message bus, more or
less independently.

Client 1
    Any app on the bus (here, called *service*). It asks the bus for sole
    custody of its preferred name, a `well-known bus name`_ that it wants
    others to recognize.

Client 2
    An interested party (here, called *watcher*). It asks the bus to emit a
    signal (send it an update) whenever *service*'s well-known bus name changes
    hands.  It uses Jeepney's ``router.filter()`` to get a message whenever this
    happens.

.. _well-known bus name: https://dbus.freedesktop.org/doc
   /dbus-specification.html#message-protocol-names
"""

import asyncio

from jeepney.io.asyncio import open_dbus_router, Proxy
from jeepney.bus_messages import MatchRule, message_bus
from jeepney.wrappers import Properties
from org_freedesktop_NetworkManager_Devices_2 import Device, Statistics
well_known_bus_name = "io.readthedocs.jeepney.aio_subscribe_example"

async def watcher(ready: asyncio.Event):

    # Create a "signal-selection" match rule
    match_rule = MatchRule(
        type="signal",
        sender=message_bus.bus_name,
        interface=message_bus.interface,
        member="PropertiesChanged",
        path=message_bus.object_path,
    )

    # Condition: arg number 0 must match the bus name (try changing either)
    #match_rule.add_arg_condition(0, well_known_bus_name)

    async with open_dbus_router() as router:
        await Proxy(message_bus, router).AddMatch(match_rule)
        with router.filter(match_rule) as q:
            print("[watcher] subscribed to PropertiesChanged signal")
            ready.set()

            msg = await q.get()
            print("[watcher] match hit:", msg.body)

async def main():
    watcher_ready = asyncio.Event()
    watcher_task = asyncio.create_task(watcher(watcher_ready))
    await watcher_ready.wait()

    async with open_dbus_router(bus="SYSTEM") as router:
        print("[service] calling 'RequestName'")
        stats_prox = Proxy(Properties(Statistics()) ,router)
        resp = await stats_prox.get_all()
        print(resp)


    await watcher_task

if __name__ == "__main__":
    asyncio.run(main())
