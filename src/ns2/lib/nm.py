from dbus_next.signature import Variant
from dbus_next.errors import DBusError
from dbus_next.aio.proxy_object import ProxyInterface
from dbus_next.aio import MessageBus
from dbus_next import Message


async def GetAllDeviceProperties(, device_path: str):

    rsp = await bus.call(
        Message(
            destination="org.freedesktop.NetworkManager",
            path=device_path,  # e.g., '/org/freedesktop/NetworkManager/Devices/1'
            interface="org.freedesktop.DBus.Properties",
            member="GetAll",
            signature="s",
            body=["org.freedesktop.NetworkManager.Device"],
        )
    )

    return rsp.body[0]


async def GetAllIP4ConfigProperties(, config_path: str):
    rsp = await bus.call(
        Message(
            destination="org.freedesktop.NetworkManager",
            path=config_path,  # e.g., '/org/freedesktop/NetworkManager/Devices/1'
            interface="org.freedesktop.DBus.Properties",
            member="GetAll",
            signature="s",
            body=["org.freedesktop.NetworkManager.IP4Config"],
        )
    )
    return rsp.body[0]


async def GetAllIP6ConfigProperties(, config_path: str):
    rsp = await bus.call(
        Message(
            destination="org.freedesktop.NetworkManager",
            path=config_path,  # e.g., '/org/freedesktop/NetworkManager/Devices/1'
            interface="org.freedesktop.DBus.Properties",
            member="GetAll",
            signature="s",
            body=["org.freedesktop.NetworkManager.IP6Config"],
        )
    )
    return rsp.body[0]


async def GetAllActiveConnectionProperties(, active_con_path: str):
    rsp = await bus.call(
        Message(
            destination="org.freedesktop.NetworkManager",
            path=active_con_path,  # e.g., '/org/freedesktop/NetworkManager/Devices/1'
            interface="org.freedesktop.DBus.Properties",
            member="GetAll",
            signature="s",
            body=["org.freedesktop.NetworkManager.Connection.Active"],
        )
    )
    return rsp.body[0]


async def GetAllActiveConnectionProperties(, active_con_path: str):
    rsp = await bus.call(
        Message(
            destination="org.freedesktop.NetworkManager",
            path=active_con_path,  # e.g., '/org/freedesktop/NetworkManager/Devices/1'
            interface="org.freedesktop.DBus.Properties",
            member="GetAll",
            signature="s",
            body=["org.freedesktop.NetworkManager.Connection.Active"],
        )
    )
    return rsp.body[0]


async def GetConnectionSettings(, connection_path: str):
    rsp = await bus.call(
        Message(
            destination="org.freedesktop.NetworkManager",
            path=connection_path,
            interface="org.freedesktop.NetworkManager.Settings.Connection",
            member="GetSettings",
            signature="",
            body=[],
        )
    )
    return rsp.body[0]


async def ConnectionUpdate2(
    , connection_path: str, settings, flags, args
):
    rsp = await bus.call(
        Message(
            destination="org.freedesktop.NetworkManager",
            path=connection_path,
            interface="org.freedesktop.NetworkManager.Settings.Connection",
            member="Update2",
            signature="a{sa{sv}}ua{sv}",
            body=[settings, flags, args],
        )
    )
    return rsp.body[0]


async def ActivateConnection(
    , connection: str, device: str, spec_obj: str
):
    rsp = await bus.call(
        Message(
            destination="org.freedesktop.NetworkManager",
            path="/org/freedesktop/NetworkManager",
            interface="org.freedesktop.NetworkManager",
            member="ActivateConnection",
            signature="sss",
            body=[connection, device, spec_obj],
        )
    )
    return rsp.body[0]


async def DeactivateConnection(, activeConnection: str):
    rsp = await bus.call(
        Message(
            destination="org.freedesktop.NetworkManager",
            path="/org/freedesktop/NetworkManager",
            interface="org.freedesktop.NetworkManager",
            member="DeactivateConnection",
            signature="s",
            body=[activeConnection],
        )
    )
    return rsp.body[0]


async def GetDeviceByIpIface(, interface: str):
    rsp = await bus.call(
        Message(
            destination="org.freedesktop.NetworkManager",
            path="/org/freedesktop/NetworkManager",
            interface="org.freedesktop.NetworkManager",
            member="GetDeviceByIpIface",
            signature="s",
            body=[interface],
        )
    )
    return rsp.body[0]


async def GetDevices():
    rsp = await bus.call(
        Message(
            destination="org.freedesktop.NetworkManager",
            path="/org/freedesktop/NetworkManager",
            interface="org.freedesktop.NetworkManager",
            member="GetDevices",
            signature="",
            body=[],
        )
    )
    return rsp.body[0]
