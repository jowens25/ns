#!/usr/bin/env python3


from nicegui import events, ui
import asyncio


async def terminal_page():

    reader, writer = await asyncio.open_unix_connection("/tmp/terminal.sock")
    terminal = ui.xterm()

    async def read_socket():
        while True:
            data = await reader.read(1024)
            if not data:
                break
            terminal.write(data.decode("utf-8", errors="ignore"))

    asyncio.create_task(read_socket())

    @terminal.on_data
    async def terminal_to_pty(event: events.XtermDataEventArguments):
        try:
            print(event.data)

            writer.write(event.data.encode("utf-8"))
            await writer.drain()

        except OSError:
            pass  # error writing to the pty; probably bash was exited
