from nicegui import ui
from systemd import journal
from datetime import datetime, timedelta
from ns2.utils import runAsyncCmdShell


# page / card for a log
async def log_page(log):
    ui.label(f"A log: {log}").classes("text-h5")
    return


# page for log overview
class ReverseReader(journal.Reader):
    def __next__(self):
        ans = self.get_previous()
        if ans:
            return ans
        raise StopIteration()


async def getSyslogIds():
    stdout, stderr = await runAsyncCmdShell(
        'journalctl --output=cat --output-fields=SYSLOG_IDENTIFIER --since "12 hours ago" | sort -u'
    )
    return [stdout]


j = journal.Reader()


levels = {
    "Only emergency": 0,
    "Alert and above": 1,
    "Critical and above": 2,
    "Error and above": 3,
    "Warning and above": 4,
    "Notice and above": 5,
    "Info and above": 6,
    "Debug and above": 7,
}


def fetch_logs(daterange, level, id) -> list[str]:
    global log

    if levels[level] >= 0:
        j.add_match("PRIORITY=0")
        log.info("using 0")

    if levels[level] >= 1:
        j.add_match("PRIORITY=1")
        log.info("using 1")
    if levels[level] >= 2:
        j.add_match("PRIORITY=2")
        log.info("using 2")
    if levels[level] >= 3:
        j.add_match("PRIORITY=3")
        log.info("using 3")
    if levels[level] >= 4:
        j.add_match("PRIORITY=4")
        log.info("using 4")
    if levels[level] >= 5:
        j.add_match("PRIORITY=5")
        log.info("using 5")
    if levels[level] >= 6:
        j.add_match("PRIORITY=6")
        log.info("using 6")
    if levels[level] >= 7:
        j.add_match("PRIORITY=7")
        log.info("using 7")

    match daterange:
        case "Last 24 hours":
            since = datetime.now() - timedelta(hours=24)
            j.seek_realtime(since)

        case "Last 7 days":
            since = datetime.now() - timedelta(days=7)
            j.seek_realtime(since)
        case "Current boot":
            j.this_boot()
            log.info("using current boot")
        case _:
            since = datetime.now() - timedelta(hours=1)
            j.seek_realtime(since)

    # j.add_match("_EXE=/usr/bin/ns-serial-mux")
    # j.seek_tail()
    for entry in j:
        # plog.info(entry)
        name = entry.get("_COMM") or entry.get("SYSLOG_IDENTIFIER")
        line = f"{entry["__REALTIME_TIMESTAMP"]} {entry["MESSAGE"]} {name}"
        log.push(line)


async def logs_page():
    global log
    ui.label("System Logs").classes("text-h5")

    with ui.card():
        with ui.row():

            def selects_change_cb():
                fetch_logs(daterange.value, level.value, identifier.value)

            daterange = ui.select(
                options=[
                    "Last 24 hours",
                    "Last 7 days",
                    "Current boot",
                    "Previous boot",
                ],
                value="Last 24 hours",
                on_change=selects_change_cb,
            )

            level = ui.select(
                value="Error and above",
                options=[
                    "Only emergency",  # 0
                    "Alert and above",  # 1
                    "Critical and above",  # 2
                    "Error and above",  # 3
                    "Warning and above",  # 4
                    "Notice and above",  # 5
                    "Info and above",  # 6
                    "Debug and above",  # 7
                ],
                on_change=selects_change_cb,
            )

            identifier = ui.select(
                value="all",
                options=["all", "lots"],
                on_change=selects_change_cb,
            )

    log = ui.log()

    fetch_logs("Last 1 hour", "Info and above", "any")

    return
