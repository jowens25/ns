import subprocess
from typing import Optional

from dataclasses import asdict, dataclass
from dbus_next.aio import MessageBus
from dbus_next import Message
from pprint import pprint

from ns2.utils import runCmd

ADMIN_GROUP = "nsadmin"
USER_GROUP = "nsuser"


@dataclass
class SystemAccount:
    UserName: Optional[str] = None
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


def _getAdmins():

    with open("/etc/group") as f:
        groupfile = f.readlines()

    for line in groupfile:
        if line.startswith(ADMIN_GROUP):
            fields = line.split(":")
            return (fields[3].strip("\n")).split(",")


def _getUsers():

    with open("/etc/group") as f:
        groupfile = f.readlines()

    for line in groupfile:
        if line.startswith(USER_GROUP):
            fields = line.split(":")
            return (fields[3].strip("\n")).split(",")


async def GetUserByName(name: str):
    u: SystemAccount
    for u in await _getUsersAndAdmins():
        n = u.get("Username")
        if n == name:
            return u


async def _getUsersAndAdmins() -> list[dict]:

    admins = _getAdmins()
    users = _getUsers()

    allUsers = []

    for a in admins:
        if a in users:
            users.remove(a)

    for u in users:

        allUsers.append({"Group": "User", "Username": u})

    for a in admins:

        allUsers.append({"Group": "Admin", "Username": a})

    return allUsers


async def _userDel(username: str):
    await runCmd(["userdel", username])


async def UserAdd(group: str, username: str):
    await runCmd(["useradd", "-g", group, "username", username])


async def _addUser(username: str):
    await runCmd(
        ["useradd", "-M", "-N", "-g", "nsuser", "-d", f"/home/{username}", username]
    )


async def _addAdmin(username: str):
    await runCmd(
        [
            "useradd",
            "-M",
            "-N",
            "-g",
            "nsadmin",
            "-G",
            "nsuser,nsadmin",
            "-d",
            f"/home/{username}",
            username,
        ]
    )


async def _setUsername(currentUsername: str, newUsername: str):
    await runCmd(["usermod", "-l", newUsername, currentUsername])


async def _setGroupUser(username: str):
    await runCmd(["usermod", "-g", "nsuser", "-G", "user", username])


async def _setGroupAdmin(username: str):
    await runCmd(["usermod", "-g", "nsadmin", "-G", "nsuser,nsadmin", username])


async def _isAdmin(username: str) -> bool:
    for a in _getAdmins():
        if a == username:
            return True
    return False


async def _deleteUser(username: str) -> str:

    admins = _getAdmins()

    users = _getUsers()

    if username in admins:
        if len(admins) > 1:
            return _userDel(username)
        else:
            return "cannot delete last admin"

    elif username in users:
        return _userDel(username)

    else:
        return "delete failed"


async def getAccountsInterface(bus: MessageBus):
    introspection = await bus.introspect("com.novus.ns", "/com/novus/ns")
    obj = bus.get_proxy_object("com.novus.ns", "/com/novus/ns", introspection)
    return obj.get_interface("com.novus.ns.accounts")
