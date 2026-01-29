from nicegui import ui, app
from theme import init_colors
from api import APIClient

#from network_manager import NM

api = APIClient(base_url="http://localhost:5000")

#nm = NM()






async def get_interfaces() -> list:
    result = await api.get("/api/v1/network/interfaces")
    if result and "interfaces" in result:

        return result


async def on_row_selected(event):
    row = event.args[1] if event.args[1] else None
    if row:
        with ui.dialog() as interface_dialog, ui.card():
            ui.label(f"Interface Details: {row['name']}").classes("text-h6 mb-4")
            await interface_card(row["name"])
            ui.button("Close", on_click=interface_dialog.close).classes("bg-secondary")

        interface_dialog.open()
        

async def network_page():

    #await nm.connect()

    with ui.column():
        interfaces = await get_interfaces()

        #res = await nm.getNetworkManger()
        #print(res)
        ui.label("Networking").classes("text-h5")

        interface_table = ui.table(
            title="Interfaces",
            rows=interfaces,
            column_defaults={
                "align": "left",
                "headerClasses": "uppercase text-primary",
            },
        )


        interface_table.add_slot('body-cell-name', '''
            <q-td :props="props">
                <a :href="'/networking/' + props.row.name" 
                   class="text-accent cursor-pointer hover:underline"
                   >
                    {{ props.value }}
                </a>
            </q-td>
        ''')


async def interface_page(interface_name: str):

    with ui.row():
        ui.link('Networking', '/networking')
        ui.label('>')
        ui.label(interface_name)



        await interface_card(interface_name)



async def interface_card(iface :str ):

    result = await api.get(f"/api/v1/network/interfaces/{iface}")
    #if result and "interface" in result:
        #print(result['interface'])

    with ui.card().classes("w-full"):
        # Header row
        with ui.row().classes("w-full items-center justify-between"):
            ui.label(iface).classes("text-h6")
            ui.label("driver info").classes("text-caption")
            ui.label("control info").classes("text-caption")
            ui.link("mac address", "#")
            ui.switch("Connected").props("disable")

        ui.separator()

        # Main content
        with ui.column().classes("w-full gap-2"):
            with ui.row().classes("items-center gap-4"):
                ui.label("Status:").classes("font-bold")
                ui.label("Active").classes("text-positive")

            with ui.row().classes("items-center gap-4"):
                ui.label("IP Address:").classes("font-bold")
                ui.label("192.168.1.100")

            with ui.row().classes("items-center gap-4"):
                ui.label("Connection:").classes("font-bold")
                ui.select(
                    ["DHCP", "MANUAL", "Static"],
                    value="DHCP",
                    on_change=update_dhcp_mode,
                )

            with ui.row().classes("items-center gap-4"):
                ui.label("DNS:").classes("font-bold")
                ui.input(placeholder="8.8.8.8").classes("flex-grow")