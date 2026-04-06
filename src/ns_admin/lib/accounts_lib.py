import subprocess
from typing import Optional

from dataclasses import asdict, dataclass
from dbus_next.aio import MessageBus
from dbus_next import Message
from pprint import pprint

from ns_admin.utils import runCmd

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


def _getAccounts() -> list[SystemAccount]:
    accounts = []
    with open("/etc/passwd", "r") as f:
        passwdFile = f.readlines()

    for i, line in enumerate(passwdFile):
        if ":" in line:
            fields = line.split(":")
            name = fields[0]
            pwd = fields[1]
            UID = fields[2]
            GID = fields[3]
            userinfo = fields[4]
            homedir = fields[5]
            shell = fields[6]
            if (
                (int(UID) < 1000 and int(UID) != 0)
                or "nologin" in shell
                or "/bin/false" in shell
            ):
                link = False

            else:
                link = True

            accounts.append(
                SystemAccount(name, pwd, UID, GID, userinfo, homedir, shell, link)
            )
    pass

    return accounts


def _getGroups() -> list[SystemGroup]:
    groups = []
    with open("/etc/group") as f:
        content = f.readlines()

    for i, line in enumerate(content):
        if ":" in line:
            if line.startswith(USER_GROUP) or line.startswith(ADMIN_GROUP):
                fields = line.split(":")
                name = fields[0]
                GID = fields[2]

                accounts = (fields[3].strip("\n")).split(",")
                num = len(accounts)
                g = SystemGroup(name, GID, num, accounts)
            groups.append(g)
    pass  # endfor

    return groups


def GetCombined():

    with open("/etc/group") as f:
        groupfile = f.readlines()

    with open("/etc/passwd") as f:
        passwdfile = f.readlines()

    for line in groupfile:
        fields = line.split(":")
        if line.startswith(USER_GROUP):
            users = (fields[3].strip("\n")).split(",")

            for user in users:
                print(user)

        if line.startswith(ADMIN_GROUP):
            admins = (fields[3].strip("\n")).split(",")

            for admin in admins:
                print(admin)


def GetGroupDict():
    return [asdict(i) for i in ReadGroupFile()]


# def GetCombinedAccountDict():
#    return [asdict(i) for n, i in CombineAccountsAndGroups().items() if i.Link]
#
#
# def GetUserByName(username):
#    return CombineAccountsAndGroups()[username]


async def ListUsers(bus: MessageBus):
    rsp = await bus.call(
        Message(
            destination="org.freedesktop.login1",
            path="/org/freedesktop/login1",
            interface="org.freedesktop.login1.Manager",
            member="ListUsers",
            signature="",
            body=[],
        )
    )

    return rsp.body[0]


async def GetUserProperties(bus: MessageBus, user_path: str):

    rsp = await bus.call(
        Message(
            destination="org.freedesktop.login1",
            path=user_path,  # e.g., '/org/freedesktop/NetworkManager/Devices/1'
            interface="org.freedesktop.DBus.Properties",
            member="GetAll",
            signature="s",
            body=["org.freedesktop.login1.User"],
        )
    )

    return rsp.body[0]


# async def getUnitProperties(bus: MessageBus, unitPath: str) -> dict:
#
#    rsp = await bus.call(
#        Message(
#            destination="org.freedesktop.systemd1",
#            path=unitPath,
#            interface="org.freedesktop.DBus.Properties",
#            member="GetAll",
#            signature="s",
#            body=["org.freedesktop.systemd1.Unit"],
#        )
#    )
#    unitProps = rsp.body[0]
#    return unitProps


async def GetUsersState(bus: MessageBus):

    for userData in await ListUsers(bus):
        print(userData)
        props = await GetUserProperties(bus, userData[2])

        # if props.get("State").value == "active":
        #    return "Logged in"
        # else:
        pprint(props)

        return

        # .get("State").value
        # settings.get('description', Variant('s', 'description not available')).value


async def UserDel(username: str):
    await runCmd(["userdel", username])


async def UserAdd(group: str, username: str):
    await runCmd(["useradd", "-g", group, "username", username])


async def _addUser(username: str):
    await runCmd(
        ["useradd", "-M", "-N", "-g", "user", "-d", f"/home/{username}", username]
    )


async def _addAdmin(username: str):
    await runCmd(
        [
            "useradd",
            "-M",
            "-N",
            "-g",
            "admin",
            "-G",
            "user,admin",
            "-d",
            f"/home/{username}",
            username,
        ]
    )


async def _setUsername(currentUsername: str, newUsername: str):
    await runCmd(["usermod", "-l", newUsername, currentUsername])


async def _setGroupUser(username: str):
    await runCmd(["usermod", "-g", "user", "-G", "user", username])


async def _setGroupAdmin(username: str):
    await runCmd(["usermod", "-g", "admin", "-G", "user,admin", username])


async def _isAdmin(username: str):
    accounts = _getAccounts()

    for a in accounts:
        pprint(a)
        input()


async def _deleteUser(username: str):
    pass
