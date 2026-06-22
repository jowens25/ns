#!/usr/bin/env python3


from nicegui import events, ui
import asyncio

from ns2.ui.control_panel import controlPanel
from ns2.utils import log


@ui.page("/terminal")
async def terminal_page():

    await controlPanel()

    terminal = ui.xterm()

    reader, writer = await asyncio.open_unix_connection("/tmp/terminal.sock")

    @terminal.on_data
    async def terminal_to_sock(event: events.XtermDataEventArguments):
        try:
            if writer:
                writer.write(event.data.encode("utf-8"))
                await writer.drain()
        except OSError:
            pass

    try:
        log.info("reading term.sock")
        while True:
            data = await reader.read(1024)
            if not data:
                break
            terminal.write(data.decode("utf-8", errors="ignore"))
    except FileNotFoundError:
        log.info("File Not Found Error: terminal socket not found.")
        pass
    except asyncio.CancelledError:
        log.info("asyncio.CancelledError - read_terminal cancelled")
        pass
    except Exception as e:
        log.info(e)
        pass
    finally:
        if writer:
            if not writer.is_closing():
                writer.close()
                await writer.wait_closed()
                writer = None
            log.info("cleaned up terminal writer")
        log.info("cleaned up terminal socket task")
