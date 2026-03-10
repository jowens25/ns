import subprocess
from typing import Optional

from dataclasses import asdict, dataclass


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
                # print(f"name: >{name}")
                # print(f"shell: >{shell}")

            # a = SystemAccount(name, pwd, UID, GID, userinfo, homedir, shell, link)
            # accounts.append(a)
            accounts[name] = SystemAccount(
                name, pwd, UID, GID, userinfo, homedir, shell, link
            )
    pass  # endfor

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
    for name, account in accounts.items():
        accountGroups = []
        for g in groups:
            if name in g.AccountString:
                accountGroups.append(g.GroupName)

        accountGroups.append(name)
        account.Groups = ", ".join(accountGroups)

    return accounts


def GetCombinedGroupDict():
    return [asdict(i) for i in CombineGroupsAndAccounts()]


def GetGroupDict():
    return [asdict(i) for i in ReadGroupFile()]


def GetAccountsDict():
    return [asdict(i) for n, i in ReadPasswdFile().items() if i.Link]


def GetCombinedAccountDict():

    return [asdict(i) for n, i in CombineAccountsAndGroups().items() if i.Link]
