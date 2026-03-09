from dataclasses import asdict, dataclass
from typing import Optional
from nicegui import ui, app
from pathlib import Path
from ns_admin.accounts_lib import *


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


async def accounts_user_page(user: str):
    # ui.label("User Configuration").classes("text-h5")
    ui.label(user).classes("text-h5")


async def accounts_page():
    """user page content"""

    ui.label("User Configuration").classes("text-h5")

    # table("Groups", GetCombinedDict(), "Name", add_group_dialog(), "Name,Id,NumLocalUsers,LocalUsers")  # Only show these
    # ui.table("Groups", , "Name", add_group_dialog(), "Name,PrimaryId,SecondaryId,Info,Home,Shell")  # Only show these

    group = SystemGroup()

    with ui.dialog() as asGroupDialog:
        with ui.card():
            ui.label("Create new group")
            errorLabel = ui.label()
            ui.input("name").bind_value(group, "GroupName")
            ui.input("id").bind_value(group, "GID")
            with ui.row():

                async def on_save_cb():
                    if group.GroupName != None and group.GID != None:
                        print(group)

                        ui.notify(addGroup(group.GroupName, group.GID))
                        # if all(validate_group([version, username, permissions, auth_type, auth_pass, priv_type, priv_pass])):
                        #    print(asdict(v3))

                        # snmp = await GetSnmp(AppBus)
                        # rsp = await snmp.call_create_v3_user(asdict(v3))
                        # rsp = await AddV3User(AppBus, asdict(v3))
                        # print(rsp)
                        # await groupsTable.refresh()
                        asGroupDialog.close()
                    else:
                        errorLabel.value = "Please correct the errors"

                        ui.notify("Please correct the errors")

                def on_cancel_cb():
                    asGroupDialog.close()

                ui.button("create", on_click=on_save_cb).props(
                    "color=accent align=center"
                )
                ui.button("cancel").props("flat color=accent dense align=center")

    with ui.expansion("Groups", icon="groups").classes("w-full"):
        groupsTable = (
            ui.table(
                title="Groups",
                rows=GetCombinedGroupDict(),
                column_defaults={
                    "align": "left",
                    "headerClasses": "uppercase text-primary",
                },
            )
            .classes("w-full")
            .props("dense")
        )

        # groupsTable.add_slot(
        #    f"body-cell-Accounts",
        #    f""" <q-td :props="props">
        #                  <a :href="'/accounts/'+ props.row.GroupName" class="text-accent cursor-pointer hover:underline"> {{{{ props.value }}}} </a>
        #                  </q-td> """,
        # )

        # with groupsTable.add_slot("body-cell-Accounts"):
        #    with groupsTable.cell("link"):
        #        ui.link().props(":href=props.value :innerHTML=props.value").classes(
        #            "text-accent"
        #        )

        groupsTable.add_slot(
            "body-cell-Accounts",
            """
        <q-td :props="props">
            <span v-for="(account, index) in props.value" :key="index">
                <span v-if="index > 0">, </span>
                <a v-if="account.link" 
                   :href="'/accounts/' + account.name" 
                   class="text-accent cursor-pointer hover:underline">
                    {{ account.name }}
                </a>
                <span v-else>{{ account.name }}</span>
            </span>
        </q-td>
        """,
        )

        # Name: Optional[str] = None
        # Id: Optional[str] = None
        # NumLocalUsers: Optional[str] = None
        # LocalUsers:

        groupsTable.props(
            f'visible-columns={"GroupName,GID,NumberOfUsers,Accounts"}'
        )  # Only show these

        with groupsTable.add_slot("top-right"):
            with ui.row():
                groupFilter = (
                    ui.input("Search for group")
                    .bind_value(groupsTable, "filter")
                    .props("align=center dense")
                )

                ui.button(
                    "Create new group", icon="add", on_click=asGroupDialog.open
                ).props("flat color=accent dense align=center")

    with ui.expansion("Accounts", icon="account_box", value=True).classes("w-full"):
        data = GetCombinedAccountDict()
        print(data)
        accountsTable = (
            ui.table(
                title="Accounts",
                rows=data,
                column_defaults={
                    "align": "left",
                    "headerClasses": "uppercase text-primary",
                },
            )
            .classes("w-full")
            .props("dense")
        )

        accountsTable.props(
            f'visible-columns={"UserName,UID,Groups"}'
        )  # Only show these

        accountsTable.add_slot(
            "header",
            r"""
              <q-tr :props="props">
                 <q-th v-for="col in props.cols" :key="col.name" :props="props"> {{ col.label }} </q-th>
                  <q-th auto-width />
              </q-tr>
          """,
        )

        async def handle_remove_service(e, zone="test"):
            print("delete: ", e.args)
            pass
            # rsp = await removeServiceFromZone(zone, e.args)
            # await zoneServicesTable.refresh()

            # ui.notify(rsp)

        accountsTable.on("remove-service", handle_remove_service)

        accountsTable.add_slot(
            "body",
            r"""
            <q-tr :props="props">
                <!-- normal columns with special handling for UserName -->
                <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    <template v-if="col.name === 'UserName'">
                        <a :href="'/accounts/' + props.row.UserName" 
                           class="text-accent cursor-pointer hover:underline">
                            {{ col.value }}
                        </a>
                    </template>
                    <template v-else>
                        {{ col.value }}
                    </template>
                </q-td>
                <!-- 3-dot menu -->
                <q-td auto-width>
                    <q-btn flat round dense icon="more_vert" color="accent">
                        <q-menu auto-close>
                            <q-list style="min-width: 150px">
                            
                            
                                <q-item clickable
                                    @click="$parent.$emit('remove-service', props.row.UserName)">
                                    <q-item-section class="text-negative">
                                        Edit user
                                    </q-item-section>
                                </q-item>  
                                
                            
                                <q-item clickable
                                    @click="$parent.$emit('remove-service', props.row.UserName)">
                                    <q-item-section class="text-negative">
                                        Log user out
                                    </q-item-section>
                                </q-item>
                                
                                <q-item clickable
                                    @click="$parent.$emit('remove-service', props.row.UserName)">
                                    <q-item-section class="text-negative">
                                        Lock account
                                    </q-item-section>
                                </q-item>  
                                
                                <q-item clickable
                                    @click="$parent.$emit('remove-service', props.row.UserName)">
                                    <q-item-section class="text-negative">
                                        Delete account
                                    </q-item-section>
                                </q-item>  
                                
                                
                            </q-list>
                        </q-menu>
                    </q-btn>
                </q-td>
            </q-tr>
            """,
        )
