from dataclasses import asdict, dataclass
from typing import Optional
from nicegui import ui, app

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



async def accounts_user_page(user: str):
    #ui.label("User Configuration").classes("text-h5")
    ui.label(user).classes("text-h5")


async def accounts_page():
    """user page content"""

    ui.label("User Configuration").classes("text-h5")

    #table("Groups", GetCombinedDict(), "Name", add_group_dialog(), "Name,Id,NumLocalUsers,LocalUsers")  # Only show these
    #ui.table("Groups", , "Name", add_group_dialog(), "Name,PrimaryId,SecondaryId,Info,Home,Shell")  # Only show these


    with ui.dialog() as asGroupDialog:
        with ui.card():
            ui.label("test")
            ui.input("name")
            ui.input("id")
            ui.button("create")
            ui.button("cancel")



    table = ui.table(
               title="Groups",
               rows=GetAccountsDict(),
               column_defaults={
                   "align": "left",
                   "headerClasses": "uppercase text-primary",
               },
           ).classes("w-full")

    table.add_slot(f'body-cell-Name', f''' <q-td :props="props">
                      <a :href="'/accounts/'+ props.row.Name" class="text-accent cursor-pointer hover:underline"> {{{{ props.value }}}} </a>
                      </q-td> ''')

    table.props(f'visible-columns={"Name,PrimaryId,SecondaryId,Info,Home,Shell"}')  # Only show these

    with table.add_slot('top-right'):
        ui.button(icon="add", on_click = asGroupDialog.open).props(
               "flat color=accent align=left").classes("w-full").props("dense")
    