from dataclasses import dataclass
from typing import Optional
from nicegui import ui

from ns2.lib.systemd1 import ListUnits


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
        if s[0] in [
            "ns-serial-mux.service",
            "ns-admin.service",
            "ns.service",
            "snmpd.service",
            "ns-agent.service",
            "nginx.service",
            "firewalld.service",
            "NetworkManager.service",
        ]:

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

    serviceUnits = MakeServicesDict(await ListUnits())
    # log.info(serviceUnits)

    servicesTable = (
        ui.table(
            title="Services",
            rows=serviceUnits,
            column_defaults={
                "align": "left",
                "headerClasses": "uppercase text-primary",
            },
        )
        .classes("w-full")
        .props("flat")
    )  # Add wrap-cells

    with servicesTable.add_slot("body-cell-Sub State"):
        with servicesTable.cell("Sub State"):
            ui.badge().props("""
                :color="props.value == 'running' ? 'green' : 'red'"
                :label="props.value"
            """)
