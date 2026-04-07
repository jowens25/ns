import asyncio
from importlib.resources import files
import logging
from systemd import journal

ASSETS_DIR = files("ns_admin") / "assets"
INTROSPECTION_DIR = files("ns_admin") / "introspection"

# sudo journalctl --output=cat --output-fields=SYSLOG_IDENTIFIER --since "12 hours ago" | sort -u


logger = logging.getLogger("ns-admin")
logger.setLevel(logging.INFO)  # This is a FILTER, not a message level
logger.addHandler(journal.JournalHandler())

logger.info("Getting started...")


async def runCmd(args: list[str]) -> str:
    print(f"running: {args}")
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode()


async def runAsyncCmd(args: list[str]) -> str:
    print(f"running: {args}")
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode()


async def runAsyncCmdShell(cmd: str) -> tuple[str, str]:
    print(f"running: {cmd}")
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode(), stderr.decode()
