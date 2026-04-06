import subprocess
from typing import Optional

from dataclasses import asdict, dataclass
from dbus_next.aio import MessageBus
from dbus_next import Message
from pprint import pprint


def addGroup(groupName, GID):
    try:
        subprocess.run(
            ["sudo", "groupadd", groupName, "-g", GID],
            check=True,
            capture_output=True,
            text=True,
        )
        return "added group"
    except subprocess.CalledProcessError as e:
        return e.stderr


def removeGroup(groupName):
    try:
        subprocess.run(
            ["sudo", "groupdel", groupName], check=True, capture_output=True, text=True
        )

        return "removed group"
    except subprocess.CalledProcessError as e:
        return e.stderr


def addUserToGroup(username, groupname):
    return subprocess.run(
        ["gpasswd", "-a", username, groupname],
        check=True,
        capture_output=True,
        text=True,
    )


def removeUserFromGroup(username, groupname):
    return subprocess.run(
        ["gpasswd", "-d", username, groupname],
        check=True,
        capture_output=True,
        text=True,
    )


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
    Accounts: Optional[list[dict]] = None
    AccountString: Optional[str] = None


def ReadPasswdFile() -> dict[SystemAccount]:
    accounts = {}
    with open("/etc/passwd", "r") as f:
        content = f.readlines()
    for i, line in enumerate(content):
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

            accounts[name] = SystemAccount(
                name, pwd, UID, GID, userinfo, homedir, shell, link
            )
    pass 

    return accounts


def ReadGroupFile() -> list[SystemGroup]:
    groups = []
    with open("/etc/group") as f:
        content = f.readlines()

    for i, line in enumerate(content):
        if ":" in line:
            fields = line.split(":")
            name = fields[0]
            GID = fields[2]

            accountsString = fields[3].strip("\n")
            # num = len(accounts)
            g = SystemGroup(name, GID, 0, [], accountsString)
            groups.append(g)
    pass  # endfor

    return groups


def CombineGroupsAndAccounts():

    groups = ReadGroupFile()

    accounts = ReadPasswdFile()

    for g in groups:
        for oa in g.AccountString.split(","):
            a = accounts.get(oa)
            if a:
                g.NumberOfUsers += 1
                g.Accounts.append({"name": a.UserName, "link": a.Link})

        for n, a in accounts.items():
            # for accountName, accountObj in accounts.items():
            if g.GID == a.GID:
                g.NumberOfUsers += 1
                g.Accounts.append({"name": a.UserName, "link": a.Link})

    return groups


def CombineAccountsAndGroups():

    groups = ReadGroupFile()

    accounts = ReadPasswdFile()

    account: SystemAccount
    name: str
    for name, account in accounts.items():
        accountGroups = []
        for g in groups:
            if g.GroupName == "root":
                continue
            if name in g.AccountString:
            
                accountGroups.append(g.GroupName)

        account.Groups = ", ".join(accountGroups)

        if "viewer" in account.Groups:
            account.Groups = "viewer"
        elif "admin" in account.Groups:
            account.Groups = "admin"

    accounts.pop("root")

    return accounts


def GetCombinedGroupDict():
    return [asdict(i) for i in CombineGroupsAndAccounts()]


def GetGroupDict():
    return [asdict(i) for i in ReadGroupFile()]


def GetAccountsDict():
    return [asdict(i) for n, i in ReadPasswdFile().items() if i.Link]


def GetCombinedAccountDict():
    return [asdict(i) for n, i in CombineAccountsAndGroups().items() if i.Link]


def GetUserByName(username):
    return CombineAccountsAndGroups()[username]


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
