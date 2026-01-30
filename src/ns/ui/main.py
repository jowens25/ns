import asyncio
from datetime import datetime
import sys
from nicegui import ui, app
from multiprocessing import freeze_support

from ns.lib.accounts import accounts_page, accounts_user_page
from ns.lib.socket import socket_stream

from ns.ui.networking_page import network_page, interface_page
from ns.ui.terminal import terminal_page
from ns.ui.theme import init_colors
from ns.ui.login import login_page
from ns.ui.root import root_page
from ns.ui.snmp_page import snmp_page, snmp_user_page
from ns.ui.ntp import ntp_page
from ns.ui.fpga_page import fpga_page
from ns.ui.tests_page import tests_page
from ns.dbus import dbus
from ns.ui.firewalld_page import firewall_page
from ns.utils import ASSETS_DIR
#
production = False

version = '0.0.1'

sock_task = None

def main():
    freeze_support()
    
    @ui.page('/networking')
    @ui.page('/networking/firewall')
    @ui.page('/networking/{interface_name}')

    @ui.page('/snmp')
    @ui.page('/snmp/{version}/{user}')

    @ui.page('/terminal')


    #@ui.page('/ntp')
    @ui.page('/accounts')
    @ui.page('/accounts/{user}')
    #@ui.page('/fpga')
    #@ui.page('/tests')
    @ui.page('/')

    @ui.page('/root')
    async def root():

        init_colors()
        if not app.storage.user.get("authenticated", False):
            ui.navigate.to("/login")
            return


        with ui.header().classes("items-center justify-between").classes("bg-dark"):
            ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
                "flat color=white"
            )
            ui.image(str(ASSETS_DIR / "NOVUS_LOGO.svg")).classes("w-48")
            ui.label(f'Welcome {app.storage.user["username"]}!')
            #ui.button("Request Admin").classes("bg-secondary").props("flat color=accent")

            label = ui.label()

            def update_date():
                label.set_text(datetime.now().astimezone().strftime('%m-%d-%Y %H:%M:%SZ'))

            ui.timer(1.0, update_date)


        async def nav(path :str):
            ui.navigate.to(path)
            width = await ui.run_javascript('window.innerWidth')
            if width < 1024:  # Adjust this breakpoint as needed
                left_drawer.hide()


        with ui.left_drawer(bordered=True).classes("bg-dark") as left_drawer:


            ui.button(
                "Networking",
                on_click=lambda:nav('/networking'),
                icon="settings_ethernet",
            ).props("flat color=white align=left").classes("full-width")


            #ui.button(
            #    "NTP",
            #    on_click=lambda: nav('/ntp'),
            #    icon="settings_ethernet",
            #).props("flat color=white align=left").classes("full-width")

            ui.button("Terminal",
                      on_click=lambda: nav('/terminal'), 
                      icon="terminal"
                      ).props("flat color=white align=left").classes("full-width")

            #ui.button(
            #    "FPGA",
            #    on_click=lambda: nav('/fpga'),
            #    icon="settings_ethernet",
            #).props("flat color=white align=left").classes("full-width")


            ui.button(
                "SNMP",
                on_click=lambda: nav('/snmp'),
                icon="settings_applications",
            ).props("flat color=white align=left").classes("full-width")

            ui.button(
                "Accounts",
                on_click=lambda: nav('/accounts'),
                icon="group",
            ).props("flat color=white align=left").classes("full-width")

            #ui.button(
            #    "Tests",
            #    on_click=lambda: nav('/tests'),
            #    icon="group",
            #).props("flat color=white align=left").classes("full-width")

            ui.separator()

            ui.button(
                "Logout",
                on_click=lambda: (app.storage.user.clear(), nav("/login")),
                icon="logout",
            ).props("flat color=negative align=left").classes("full-width")

        # Footer
        with ui.footer().classes("bg-dark"):
            ui.label(version)


        ui.sub_pages({
            '/': network_page,
            '/networking': network_page, 
            '/networking/firewall': firewall_page,
            '/networking/{interface_name}': interface_page,
            '/ntp' : ntp_page,
            '/snmp': snmp_page, 
            '/snmp/{version}/{user}': snmp_user_page,
            '/accounts': accounts_page, 
            '/accounts/{user}': accounts_user_page,
            '/terminal': terminal_page,
            #'/fpga': fpga_page,
            #'/tests': tests_page
            }).classes("w-full")




    
    @app.on_startup
    async def startup():
        global sock_task
        await dbus.setup()
        sock_task = asyncio.create_task(socket_stream())


    @app.on_shutdown
    async def shutdown():
        global sock_task
        await dbus.cleanup()
        #await socket_cleanup()
        sock_task.cancel()
    

    if not sys.argv[1]:
        sys.exit()

    ui.run(
       port=int(sys.argv[1]),
       reload=False,
       storage_secret="your-secret-key",
       title="Novus Configuration Tool",
       #favicon=str(ASSETS_DIR / "favicon.png")
       )
       



if __name__ in {"__main__", "__mp_main__"}:
    main()
    
   

#TODO Clean up and test ipv4 stuff, expand to dns and ipv6
#TODO Add firewalld to networking page
#TODO Move snmp to a separate service for permissions
#TODO Work on accounts and grouping users into accounts
#TODO Implement Policy kit one day
#TODO Move time server stuff to dbus service?
#TODO Move PAM / Auth to a different service
#TODO Fix terminal to be in the signed in user