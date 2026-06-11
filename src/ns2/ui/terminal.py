#!/usr/bin/env python3


from nicegui import events, ui, app
import asyncio


async def terminal_page():
    reader, writer = await asyncio.open_unix_connection("/tmp/terminal.sock")
    terminal = ui.xterm()
    task = None

    async def read_socket():
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                terminal.write(data.decode("utf-8", errors="ignore"))
        except asyncio.CancelledError:
            pass  # graceful shutdown

    task = asyncio.create_task(read_socket())

    async def cleanup():
        if task and not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

        if not writer.is_closing():
            writer.close()
            await writer.wait_closed()

    # Fires when this client disconnects or navigates away
    app.on_disconnect(cleanup)

    @terminal.on_data
    async def terminal_to_pty(event: events.XtermDataEventArguments):
        try:
            writer.write(event.data.encode("utf-8"))
            await writer.drain()
        except OSError:
            pass
