
from nicegui import ui, app, background_tasks, events

import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px

import plotly.io as pio
pio.templates.default = "plotly_dark"

from network_delay import get_network_delay_data_locally, calculate_last_50_jitter, get_files_to_view, get_data_by_name


    
def set_selected_file(f):
    global selected_file
    selected_file = f

async def tests_page():
    global selected_file
    
    try:
        selected_file = get_files_to_view()[0]['href']
    except Exception as e:
        print(e)

    with ui.column():
        with ui.row() as pageContainer:
            ui.label("Network Delay Test Data").classes("text-h5")
            
        with ui.column():
            for r in get_files_to_view():
                ui.button(r["href"], on_click=lambda f=r['href']: set_selected_file(f)).classes('bg-accent')

        with ui.row():

            def build_plot():
                
                #start, ts, delays = get_network_delay_data_locally()

                start, ts, delays = get_data_by_name(selected_file)
                #delays = [0]
                #start = ''

                f1 = go.Figure(go.Scatter(x=list(range(len(delays))),y=delays))
                f2 = go.Figure(px.histogram(x=delays))
                jitter = calculate_last_50_jitter(delays)
                f1.update_xaxes(title_text=f"Samples - Jitter on last 50: {jitter}")
                f1.update_yaxes(title_text="RTT (Delay) (ms)")

                f1.update_layout(title_text=f"Ping Over VPN Test Started: {start}")

                mean = np.mean(delays)
                std = np.std(delays)
                f2.update_layout(title_text=f"Mean: {mean} STD: {std}")

                #fig.update_layout(title_text="Pinging home server from novus",margin=dict(l=0, r=0, t=0, b=0))

                p1 = ui.plotly(f1).classes("w-full")
                p2 = ui.plotly(f2).classes("w-full")

                return f1, p1, f2 , p2
            f1, p1, f2, p2 = build_plot()


            def update_plots():
                start, ts, delays = get_data_by_name(selected_file)
                #_, ts, delays = get_network_delay_data_locally()
                jitter = calculate_last_50_jitter(delays)
                f1.update_layout(title_text=f"Ping Over VPN Test Started: {start}")

                f1.update_xaxes(title_text=f"Samples - Jitter on last 50: {jitter}")
                f1.data[0].x = list(range(len(delays)))
                f1.data[0].y = delays

                f2.data[0].x = delays

                p1.update()
                p2.update()
                mean = np.mean(delays)
                std = np.std(delays)
                f2.update_layout(title_text=f"Mean: {mean} STD: {std}")



            timer = ui.timer(5, callback=update_plots)

            def toggle_timer():
                if timer.active:
                    timer.deactivate()
                else:
                    timer.activate()

        
            def get_down_latest():

                _, ts, delays = get_data_by_name(selected_file)

                data = {"ts": ts, "rtt": delays}

                df = pd.DataFrame(data)

                df.to_excel("temp.xlsx", index=False, header=True)

                ui.download.file('temp.xlsx')

            
        ui.button("Toggle Refresh", on_click=toggle_timer).classes("bg-accent")

        ui.button("Download selected", on_click=get_down_latest ).classes("bg-accent")


            

