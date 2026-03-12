from nicegui import ui


# page / card for a log
async def log_page(log):
    ui.label(f"A log: {log}").classes("text-h5")
    return


# page for log overview


async def logs_page():
    ui.label("Logs").classes("text-h5")
    return
