import asyncio
from importlib.resources import files
import logging
from systemd import journal
import sys

ASSETS_DIR = files("ns2") / "assets"

# sudo journalctl --output=cat --output-fields=SYSLOG_IDENTIFIER --since "12 hours ago" | sort -u


log = logging.getLogger("ns-admin")
log.setLevel(logging.INFO)  # This is a FILTER, not a message level
log.addHandler(journal.JournalHandler())
log.addHandler(logging.StreamHandler(sys.stdout))
log.addHandler(logging.FileHandler("debug.log"))


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
