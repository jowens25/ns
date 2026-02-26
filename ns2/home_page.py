from nicegui import ui, app

from ns2.networking import get_device_statistics, getDevices, get_device_properties, set_refresh_rate
from ns2.dbus import get_dbus
from ns2.ns_socket import *


import plotly.graph_objects as go
import plotly.express as px

import plotly.io as pio
pio.templates.default = "plotly_dark"



rx = []
tx = []

rx_mbs = []
tx_mbs = []

async def home_page():

    with ui.card():

        #with ui.column():
            with ui.row():
                def build_plots():
                        f1 = go.Figure(go.Scatter(x=list(range(len(rx_mbs))),y=rx_mbs)).update_layout(title_text=f"Mbps Receiving" ,  margin=dict(l=10, r=10, t=50, b=10))
                        p1 = ui.plotly(f1).classes('h-32')

                        f2 = go.Figure(go.Scatter(x=list(range(len(tx_mbs))),y=tx_mbs)).update_layout(title_text=f"Mbps Transmitting",  margin=dict(l=10, r=10, t=50, b=10))
                        p2 = ui.plotly(f2).classes('h-32').props('dense')
                        return f1, p1, f2, p2

                f1, p1, f2, p2 = build_plots()

                async def update_plots():
                    global rx_mbs
                    global tx_mbs
                    AppBus = await get_dbus()
                    device_paths = await getDevices(AppBus)
                    for d in device_paths:
                        props = await get_device_properties(AppBus, d)
                        if props['DeviceType'].value in [1]:
                            await set_refresh_rate(AppBus, d, 1000)

                            stats = await get_device_statistics(AppBus, d)

                            #print(stats)

                    rx.append(stats['rx_bytes'])
                    tx.append(stats['tx_bytes'])
                    if len(rx) > 2:
                        rx_mbs.append((rx[-1]-rx[-2])/1000000)
                        tx_mbs.append((tx[-1]-tx[-2])/1000000)

                    if len(rx_mbs)>=120:
                        rx_mbs = rx_mbs[-120:]                    
                        tx_mbs = tx_mbs[-120:]
                        



                    f1.data[0].x = list(range(len(rx_mbs)))
                    f1.data[0].y = rx_mbs
                    p1.update()
                    
                    f2.data[0].x = list(range(len(tx_mbs)))
                    f2.data[0].y = tx_mbs
                    p2.update()

    timer = ui.timer(1, callback=update_plots)

    with ui.card():
        with ui.row():
            term = ui.xterm({'convertEol': True})
            socket_receive.subscribe(lambda _data: term.write(_data))




        