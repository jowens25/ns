from dataclasses import asdict, dataclass
from typing import Optional
from nicegui import ui, app

from ns2.lib.systemd1 import *
from ns2.api.dbus import get_dbus


@dataclass
class SystemdUnit:  # ssssssouso
    PrimaryName: Optional[str] = None
    Description: Optional[str] = None
    LoadState: Optional[str] = None
    ActiveState: Optional[str] = None
    SubState: Optional[str] = None
    FollowedUnit: Optional[str] = None
    UnitPath: Optional[str] = None
    JobId: Optional[str] = None
    JobType: Optional[str] = None
    JobPath: Optional[str] = None


def MakeServicesDict(servs):

    services = []

    for s in servs:
        if s[0].endswith(".service"):

            services.append(
                {
                    "Name": s[0].strip(),
                    # "Description": s[1],
                    "Load State": s[2],
                    "Active State": s[3],
                    "Sub State": s[4],
                }
            )

    return services

    # return [asdict(SystemdUnit(s)) for s in services]


async def services_page():

    serviceUnits = MakeServicesDict(await ListUnits(await get_dbus()))
    # print(serviceUnits)

    servicesTable = (
        ui.table(
            title="Services",
            rows=serviceUnits,
            column_defaults={
                "align": "left",
                "headerClasses": "uppercase text-primary",
            },
        )
        # Full width
        .classes("w-full")  # Add wrap-cells
    )


# async def addServiceDialog(zoneName):
#    with ui.dialog() as dialog:
#        with ui.card().props("flat").classes("w-full"):
#            ui.label(f"Add services to {zoneName}").classes("text-h5")
#
#            # selectedServices = ui.input_chips('Allowed services', new_value_mode='add-unique', clearable=True).props('disable-input')
#            tab = await serviceSelectionTable()
#
#            async def on_add_cb():
#                print(tab.selected)
#                for service in tab.selected:
#                    serviceName = service["Service"]
#                    rsp = await addServiceToZone(zoneName, serviceName)
#                    await zoneServicesTable.refresh()
#                dialog.close()
#
#                ui.notify(rsp)
#
#            with ui.row():
#                ui.button("Add", on_click=on_add_cb).props("color=accent align=left")
#                ui.button("Cancel", on_click=dialog.close).props(
#                    "flat color=accent align=left"
#                )
#
#    return dialog
