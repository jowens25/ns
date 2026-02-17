from dataclasses import asdict, dataclass
from typing import Optional

@dataclass
class SystemAccount:
    Name: Optional[str] = None
    PrimaryId: Optional[str] = None
    SecondaryId: Optional[str] = None
    Info: Optional[str] = None
    Home: Optional[str] = None
    Shell: Optional[str] = None

@dataclass
class SystemGroup:
    Name: Optional[str] = None
    Id: Optional[str] = None
    NumLocalUsers : Optional[str] = None
    LocalUsers : Optional[str] = None

def ReadPasswordsFile() -> list[SystemAccount]:
    accounts = []
    with open("/etc/passwd", "r") as f:
        content = f.readlines()
    for i, line in enumerate(content):
        if ":" in line:
            fields = line.split(":")
            name = fields[0]
            primaryId = fields[2]
            secondaryId = fields[3]
            info = fields[4]
            home = fields[5]
            shell = fields[6]
            a = SystemAccount(name, primaryId, secondaryId, info, home, shell)
            accounts.append(a)
    pass #endfor

    return accounts


def ReadGroupFile() -> list[SystemGroup]:
    groups = []
    with open("/etc/group") as f:
        content = f.readlines()

    for i, line in enumerate(content):
        if ":" in line:
            fields = line.split(":")
            name = fields[0]
            id = fields[2]
            accounts = fields[3].strip("\n")
            num = len(accounts.split(","))
            g = SystemGroup(name, id, num, accounts)
            groups.append(g)
    pass #endfor

    return groups


def CombineGroupsAndAccounts():
    accounts = ReadPasswordsFile()
    groups = ReadGroupFile()

    newgroups = []
    for g in groups:
        for a in accounts:
            if g.Id == a.SecondaryId:
                g.NumLocalUsers += 1
                g.LocalUsers += f",{a.Name}"

        newgroups.append(g)

    return newgroups

def GetCombinedDict():
    return [asdict(i) for i in CombineGroupsAndAccounts()]



def GetGroupDict():
    return [asdict(i) for i in ReadGroupFile()]

def GetAccountsDict():
    return [asdict(i) for i in ReadPasswordsFile()]


