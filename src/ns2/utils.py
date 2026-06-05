import asyncio
from importlib.resources import files
import logging
from systemd import journal
import sys

ASSETS_DIR = files("ns2") / "assets"

# sudo journalctl --output=cat --output-fields=SYSLOG_IDENTIFIER --since "12 hours ago" | sort -u


log = logging.getLogger("ns-admin")
log.setLevel(logging.INFO)  # This is a FILTER, not a message level
log.addHandler(journal.JournalHandler(SYSLOG_IDENTIFIER="ns-admin"))
log.addHandler(logging.StreamHandler(sys.stdout))
#log.addHandler(logging.FileHandler("debug.log"))


async def runCmd(args: list[str]) -> str:
    log.info(f"running: {args}")
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode()


async def runAsyncCmd(args: list[str]) -> str:
    log.info(f"running: {args}")
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode()


async def runAsyncCmdShell(cmd: str) -> tuple[str, str]:
    log.info(f"running: {cmd}")
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode(), stderr.decode()


def validate_group(group: list):
    return [x.validate() for x in group]


def make_col_of(l: str, label:str|None = None) -> dict:
    if label:
        return {"name": l, "label": label, "field": l}
    return {"name": l, "label": l, "field": l}


def make_action_col() -> dict:
    return {"name": "action", "label": "", "align": "center"}


def add_header_slot(tab):
    return tab.add_slot(
        "header",
        r"""
          <q-tr :props="props">
             <q-th v-for="col in props.cols" :key="col.name" :props="props"> {{ col.label }} </q-th>
              <q-th auto-width />
          </q-tr>
      """,
    )
