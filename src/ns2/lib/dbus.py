from dbus_next.aio import MessageBus
from dbus_next import Message
from dbus_next.constants import BusType


async def Call(zoneName: str, interfaceName: str):

    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    rsp = await bus.call(
        Message(
            destination="org.fedoraproject.FirewallD1",
            path="/org/fedoraproject/FirewallD1",
            interface="org.fedoraproject.FirewallD1.zone",
            member="addInterface",
            signature="ss",
            body=[zoneName, interfaceName],
        )
    )
    return rsp.body[0]
