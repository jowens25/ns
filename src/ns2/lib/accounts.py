from dataclasses import dataclass
from typing import Optional

from dbus_next import Message

from ns2.lib.bridge import BridgeCall


@dataclass
class SystemAccount:
    Username: Optional[str] = None
    Password: Optional[str] = None
    UID: Optional[str] = None
    GID: Optional[str] = None
    UserInfo: Optional[str] = None
    HomeDir: Optional[str] = None
    Shell: Optional[str] = None
    Link: Optional[bool] = False
    Groups: Optional[str] = None


@dataclass
class SystemGroup:
    GroupName: Optional[str] = None
    GID: Optional[str] = None
    NumberOfUsers: Optional[str] = None
    Accounts: Optional[list[str]] = None


async def GetUsers() -> Message:
    rsp = await BridgeCall(
        destination="com.novus.ns",
        path="/com/novus/ns",
        interface="com.novus.ns.accounts",
        member="GetUsers",
        signature="",
        body=[],
    )

    return rsp


async def ValidatePassword(password: str) -> Message:
    rsp = await BridgeCall(
        destination="com.novus.ns",
        path="/com/novus/ns",
        interface="com.novus.ns.accounts",
        member="ValidatePassword",
        signature="s",
        body=[password],
    )

    return rsp
