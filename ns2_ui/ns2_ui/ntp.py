from ns2.ns_socket import *
from nicegui import ui, events

import plotly.graph_objects as go
import ns2.dbus


from ns2.ntl import NtpServerProperties




async def writeNtlConfig(content: str):
    content.splitlines()
    for line in content.splitlines():
        if line.startswith("$WC"):
            await write_socket(line)

def parse_lines_for_num(lines :list[str]) -> list:
    frequencies = []

    line: str
    for line in lines:
        if line.startswith("$GPNVS,9,"):
            fields = line.split(',')
            freq = fields[2].strip('+')
            frequencies.append(float(freq))
    
    return frequencies





async def ntp_page():
    with ui.column() as pageContainer:
        ui.label("NTP").classes("text-h5")
        with ui.row():
            term = ui.xterm({'convertEol': True})

            
            socket_receive.subscribe(lambda _data: term.write(_data))


            #term.on_data(lambda e: term.write(e.data.replace('\r', '\n\r').replace('\x7f', '\x1b[0D\x1b[0K')))

            with ui.card():
                async def handle_upload(e: events.UploadEventArguments):
                    ui.notify(f'Uploaded {e.file.name}')
                    await WriteConfig(await e.file.text())
    
                ui.upload(label="FPGA Config Upload", on_upload=handle_upload).props("flat color=accent")
            



        def build_plot():
            # initial read
            with open('data.txt', 'r') as f:
                lines = f.readlines()
            y = parse_lines_for_num(lines)

            fig = go.Figure(go.Scatter(x=list(range(len(y))),y=y))
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

            plot = ui.plotly(fig).classes('w-full h-40')
            return plot, fig

        plot, fig = build_plot()

        def refresh_plot():
            # re-read file and update trace data
            with open('data.txt', 'r') as f:
                lines = f.readlines()
            y = parse_lines_for_num(lines)

            # update the existing figure instead of creating a new one
            fig.data[0].y = y
            plot.update()

        # call this whenever you get new data
        #socket_received.subscribe(lambda _data: refresh_plot())

        ui.timer(1, refresh_plot)
        
        @ui.refreshable
        async def ntp_card():
            with ui.card():
                ui.button("read ntp stuff", on_click=ntp_card.refresh).props("flat color=accent align=left")

                ntpProps = await ReadNtlProperties(22, NtpServerProperties)
                
                
                ui.json_editor({'content': {'json': ntpProps}},
                    on_select=lambda e: ui.notify(f'Select: {e}'),
                    on_change=lambda e: ui.notify(f'Change: {e}'))
             

        await ntp_card()

        




