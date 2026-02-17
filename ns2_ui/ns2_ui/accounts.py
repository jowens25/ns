from nicegui import ui, app

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
    