import asyncio
from dbus_next.signature import Variant
from ns2.lib.bridge import BridgeCall, GetBridge
from ns2.utils import log
from ns2.lib.bridge import BusCall


async def CallListTimezones() -> list[str]:

    rsp = await BusCall(
        destination="org.freedesktop.timedate1",
        path="/org/freedesktop/timedate1",
        interface="org.freedesktop.timedate1",
        member="ListTimezones",
        signature="",
        body=[],
    )

    return rsp.body[0]


async def CallSetTimezone(tz: str):

    await BusCall(
        destination="org.freedesktop.timedate1",
        path="/org/freedesktop/timedate1",
        interface="org.freedesktop.timedate1",
        member="SetTimezone",
        signature="sb",
        body=[tz, False],
    )

    return None


async def CallGetTimezone() -> str:
    rsp = await BusCall(
        destination="org.freedesktop.timedate1",
        path="/org/freedesktop/timedate1",
        interface="org.freedesktop.DBus.Properties",
        member="Get",
        signature="ss",
        body=["org.freedesktop.timedate1", "Timezone"],
    )
    return rsp.body[0].value
