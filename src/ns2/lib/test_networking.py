# from pprint import pprint
# from ns2.lib.accounts import GetUsers

# import asyncio


# from ns2.lib.bridge import CallMakeBridge, SetupBridge, CleanupBridge, GetBridge
# from ns2.lib.networking import *

# from dbus_next import Message


# from dataclasses import dataclass, asdict
# import asyncio
# from nicegui import Event, app


# from ns2.utils import log

# socket_path = "/var/lib/ns/serial.sock"

# socket_receive = Event()

# socket_open = False


# async def main(max_string: int):
#     reader, writer = await asyncio.open_unix_connection(socket_path)

#     for i in range(max_string + 1):
#         cmd = f"$NVS{i}=1\r\n"
#         log.info("sending: ", cmd)
#         writer.write(cmd.encode())
#         await writer.drain()

#     writer.close()
#     await writer.wait_closed()


# def set_status_string(status, num):
#     return f"$NVS{int(num)}={int(status)}"


# async def listen_to(path):

#     socket_path = path
#     reader, writer = await asyncio.open_unix_connection(socket_path)
#     while True:
#         line = await reader.readline()
#         if line:
#             log.info(line.decode("utf-8", errors="ignore").strip("\r\n"))


# async def read_socket(reader, cmd, timeout=1):

#     rsps = []

#     try:
#         async with asyncio.timeout(timeout):
#             while True:
#                 line = await reader.readline()

#                 if not line:
#                     break

#                 line = line.decode("utf-8")

#                 if line.startswith(cmd):
#                     rsps.append(line)
#                     break

#     except TimeoutError:

#         pass

#     return rsps


# async def read_write_socket(cmd: str) -> str:

#     socket_path = "/var/lib/ns/serial.sock"
#     reader, writer = await asyncio.open_unix_connection(socket_path)

#     read_task = asyncio.create_task(read_socket(reader, cmd))

#     writer.write((cmd + "\r\n").encode())
#     await writer.drain()

#     responses = await read_task

#     writer.close()

#     await writer.wait_closed()

#     return "".join(responses)


# async def socket_stream():
#     global socket_open
#     try:
#         reader, writer = await asyncio.open_unix_connection(socket_path)
#         log.info("SOCKET OPENED")
#         socket_open = True
#         while True:
#             line = (await reader.readline()).decode("utf-8", errors="ignore")
#             if line:
#                 # yield line
#                 socket_receive.emit(line)
#                 # record_line(line)
#             else:
#                 break
#     except FileNotFoundError:
#         log.info("SOCKET NOT AVAILABLE")
#         # self.socket_received.emit("Socket Not Available")
#         socket_open = False
#         raise
#     except asyncio.CancelledError:
#         log.info("SOCKET LISTENER CANCELLED")
#         socket_open = False
#         if writer:
#             writer.close()
#             await writer.wait_closed()
#         raise
#     finally:
#         log.info("SOCKET LISTENER CLOSED")
#         socket_open = False
#         if writer:
#             writer.close()
#             await writer.wait_closed()


# #
# # def message_handler(msg: Message):
# #
# #    if msg.interface == "com.novus.ns.accounts" and msg.member == "ValidatePassword":
# #        log.info(msg.body)
# #        return Message.new_method_return(msg, "s", ["got it"])
# #
# #
# # async def TestFunc():
# #    log.info("running test?")
# #
# #    log.info("setup bridge as: ", await SetupBridge("admin"))
# #    await asyncio.sleep(1)
# #
# #    bridge = GetBridge()
# #
# #    rsp = await BridgeCall(
# #        destination="org.freedesktop.DBus",
# #        path="/org/freedesktop/DBus",
# #        interface="org.freedesktop.DBus",
# #        member="AddMatch",
# #        signature="s",
# #        body=[
# #            "type='signal',member='ValidatePassword',interface='com.novus.ns.accounts'"
# #        ],
# #    )
# #
# #    log.info(rsp.body)
# #
# #    bridge.add_message_handler(message_handler)
# #
# #    while True:
# #        await asyncio.sleep(1)
# #
# #    await CleanupBridge()
# #
# #    # device_path = await GetDeviceByIpIface("enp3s0")
# #    #
# #    # ip4_config_path = await GetNmProp(device_path, "Device", "Ip4Config")
# #    # ip4AddressData = await GetNmProp(
# #    ip4_config_path, "IP4Config", "AddressData", "aa{sv}"
# # )
# #
# # log.info(ip4AddressData)

# # rsp = await GetAppliedConnection(device_path, 0)
# #
# # log.info(rsp)

# # log.info(await GetInterfaceData("enp3s0"))
# # rsp = await SystemdRestart("snmpd.service")

# # log.info(rsp)

# # devices = await DbusCall(
# #    bridge,
# #    destination="org.freedesktop.NetworkManager",
# #    path="/org/freedesktop/NetworkManager",
# #    method="org.freedesktop.NetworkManager.GetDevices",
# #    args=[],
# #    signature=None,
# # )
# # plog.info(devices)
# #
# # log.info(devices[1])
# #
# # plog.info(
# #    await DbusCall(
# #        bridge,
# #        destination="org.freedesktop.NetworkManager",
# #        path="/org/freedesktop/NetworkManager/Devices/2",
# #        method="org.freedesktop.NetworkManager.Device.GetAppliedConnection",
# #        args=["0"],
# #        signature=["u"],
# #    ),
# # )

# # plog.info(
# #    await DbusCall(
# #        bridge,
# #        destination="org.freedesktop.NetworkManager",
# #        path="/org/freedesktop/NetworkManager",
# #        method="org.freedesktop.NetworkManager.Enable",
# #        args=[False],
# #        # signature=["b"],
# #    ),
# # )


# #
# # prop = await DbusCall(
# #    bridge,
# #    destination="org.freedesktop.NetworkManager",
# #    path=devices[1],
# #    method="org.freedesktop.DBus.Properties.Get",
# #    args=["org.freedesktop.NetworkManager.Device", "ActiveConnection"],
# # )
# #
# # log.info(prop)

# # await bridge.disconnect()
# # await CallCloseBridge()


# if __name__ == "__main__":

#     asyncio.run(TestFunc())


# #


# # log.info("no test run")
# # CheckBridge
# # asyncio.run(CheckBridge())

# # log.info(
# #    bridgeCall(
# #        "com.novus.ns",
# #        "/com/novus/ns",
# #        "com.novus.ns.pam",
# #        "GetStuff",
# #        [],
# #    )
# # )
# #
# # log.info(
# #    bridgeCall(
# #        "com.novus.ns",
# #        "/com/novus/ns",
# #        "com.novus.ns.pam",
# #        "Authenticate",
# #        ["jowens", "jowens"],
# #    )
# # )
# #
# #    devices = bridgeCall(
# #        destination="org.freedesktop.NetworkManager",
# #        path="/org/freedesktop/NetworkManager",
# #        method="org.freedesktop.NetworkManager.GetDevices",
# #        args=[],
# #    )
# #
# #    log.info(devices)
# #
# #    log.info(
# #        "state: ",
# #        bridgeCall(
# #            destination="org.freedesktop.NetworkManager",
# #            path="/org/freedesktop/NetworkManager",
# #            method="org.freedesktop.DBus.Properties.Get",
# #            args=["org.freedesktop.NetworkManager", "State"],
# #        ),
# #    )
# #
# #    prop = bridgeCall(
# #        destination="org.freedesktop.NetworkManager",
# #        path=devices[1],
# #        method="org.freedesktop.DBus.Properties.Get",
# #        args=["org.freedesktop.NetworkManager.Device", "ActiveConnection"],
# #    )
# #
# #    log.info(prop)

# # bridgeCall(
# #    # Message(
# #    destination="org.freedesktop.NetworkManager",
# #    path=devices[1],
# #    iface="org.freedesktop.NetworkManager.Device.Statistics",
# #    method="Get",
# #    # signature="ssv",
# #    args=[],
# #    # )
# # )

# # log.info(
# #    "allowed? result:",
# #    bridgeCall(
# #        destination="com.novus.ns",
# #        path="/com/novus/ns",
# #        method="com.novus.ns.pam.GetStuff",
# #        args=[],
# #    ),
# # )
