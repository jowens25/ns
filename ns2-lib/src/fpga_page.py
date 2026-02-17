import asyncio
from nicegui import ui, app, background_tasks, events
from ns2.commands import runAsyncCmd
import os


async def fpga_page():
    with ui.column() as pageContainer:
        ui.label("FPGA Bitstream flasher").classes("text-h5")
        with ui.row():

            with ui.card():
                async def handle_upload(e: events.UploadEventArguments):
                    ui.notify(f'Uploaded {e.file.name}', type='positive')
                    file_path = os.path.join("bitstreams", e.file.name)
                    await e.file.save(file_path)

                    res = await runAsyncCmd(["sudo", "xc3sprog", "-c", "ftdi", file_path])
                    ui.notify(f'Flashed {res}', type='positive')

                ui.upload(label="FPGA Config Upload", on_upload=handle_upload).props("flat color=accent")
            


