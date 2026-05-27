from dbus_next.aio import MessageBus
from dbus_next import Message
import asyncio
from ns2.lib.bridge import *


async def test_tcp():

    await SetupBridge("tech")

    print(await GetActiveUser())


if __name__ == "__main__":

    asyncio.run(test_tcp())
