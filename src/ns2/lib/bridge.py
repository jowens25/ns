import asyncio
import json
import os
from pprint import pprint
from websockets.asyncio.client import connect
from websockets import ClientConnection

# i think we are going to just make different types of json packets do what we need:
#
# {"dbus":dbuscall}
# {"cmd":commandcall}
# {"systemd":systemdcall}
from dbus_next import Message
from dbus_next.constants import BusType
from dbus_next.aio import MessageBus

from ns2.lib.dbus import *


class Bridge:
    def __init__(self):
        self.conn = None
        self.messages = asyncio.Queue(10)
        self.id = 0
        self.requests = asyncio.Queue(10)
        self.responses = asyncio.Queue(10)
        self.isConnected = False
        self.rxing = None
        self.txing = None

    async def connect(self):
        self.conn = await connect("ws://localhost:3000/bridge")
        self.rxing = asyncio.create_task(self.receive())
        self.txing = asyncio.create_task(self.send())
        self.isConnected = True

    async def disconnect(self):
        if self.conn:
            await self.conn.close()
            self.isConnected = False

    async def cleanup(self):
        if self.isConnected:
            self.rxing.cancel()
            self.txing.cancel()
            await self.disconnect()

    async def setup(self) -> bool:
        self.connect()

    async def send(self):
        while True:
            request = await self.requests.get()
            await self.conn.send(json.dumps(request))

    async def receive(self):
        msg: dict
        async for msg in self.conn:
            msg = json.loads(msg)
            # print(msg)
            if msg.get("id", None):
                # print("got resp")
                await self.responses.put(msg)
            else:
                # print("got mes")
                await self.messages.put(msg)

    async def getMessage(self):
        return await self.messages.get()

    async def getResponse(self, id) -> dict:
        while True:
            try:
                async with asyncio.timeout(0.10):
                    rsp = await self.responses.get()
                    if int(rsp.get("id", None)) == id:
                        return rsp
                    else:
                        await self.responses.put(rsp)
            except TimeoutError:
                return {"error", "no matching response"}

    async def sendRequest(self, req) -> int:
        self.id += 1
        req["id"] = str(self.id)
        await self.requests.put(req)
        return self.id

    async def writeRead(self, msg: dict) -> dict:
        id = await self.sendRequest(msg)
        return await self.getResponse(id)

    async def checkBridge(self) -> bool:
        """checks to make sure its up"""
        rsp = await self.writeRead({"status": "?"})
        print(rsp)
        if rsp["status"] == "up":
            return True
        return False


UserBridge = None


async def SetupBridge(_username: str) -> str:
    """on new user session create new bridge, cancel old one?, returns connected instance"""
    # 1. get ref, clean it up
    # 2. new ref, build it for user
    # 3. connect, check connection
    # 4. if its good return name, else false...?
    currentBridge = GetBridge()
    if currentBridge:
        await currentBridge.cleanup()

    bridge = Bridge()

    await CallMakeBridge(_username)
    await asyncio.sleep(0.5)
    await bridge.connect()

    if bridge.isConnected:
        print("new bridge connected")
        SetBridge(bridge)
        return await GetActiveUserBridge(bridge)
    else:
        return False


def GetBridge():
    global UserBridge
    return UserBridge


def GetNewBridge():
    global UserBridge
    if UserBridge is not None:
        return UserBridge
    else:
        bridge = Bridge()
        return bridge


def SetBridge(bridge: Bridge):
    global UserBridge
    UserBridge = bridge


async def CheckBridge() -> bool:
    """checks to make sure its up"""
    bridge = GetBridge()

    if not bridge:
        return False

    rsp = await bridge.writeRead({"status": "?"})
    print(rsp)
    if rsp["status"] == "up":
        return True
    return False


async def GetActiveUserBridge(bridge) -> str:
    rsp: dict
    rsp = await bridge.writeRead({"activeUser": "?"})
    return rsp.get("activeUser", None)


async def tryBridge():

    await CallMakeBridge("admin")

    await asyncio.sleep(1)

    print(await GetBridgePid())

    bridge = Bridge()
    await bridge.connect()

    print(await bridge.send({"test1": "hi", "test2": "hi"}))

    await asyncio.sleep(2)

    await bridge.disconnect()

    await CallCloseBridge()


async def SnmpCall(meth, args):
    return await DbusCall(
        "com.novus.ns", "/com/novus/ns", "com.novus.ns.snmp", meth, "", args
    )


async def DbusCall(
    destination: str,
    path: str,
    interface: str,
    member: str,
    signature: str,
    args,
    returnSignature: str = "",
):

    if type(args) != list:
        print("CHECK INPUT OF: ", member)
        # return

    method = interface + "." + member

    bridge = GetBridge()

    req = {
        "dbusCall": "1",
        "destination": destination,
        "path": path,
        "method": method,
        "args": args,
        "signature": signature,
        "returnsignature": returnSignature,
    }

    # print("REQUEST: ")
    # pprint(req)

    rsp = await bridge.writeRead(req)

    # print(rsp)
    err = rsp.get("dbusError", None)
    if err is not None:
        print(err)
        # input()
        exit(-1)

    err = rsp.get("error", None)
    if err is not None:
        print(err)
        exit(-2)

    # print("RESPONSE: ")
    # pprint(rsp)

    return rsp.get("dbusResponse")


async def WriteBridge(req: dict):

    bridge = GetBridge()

    rsp = await bridge.writeRead(req)

    return rsp
