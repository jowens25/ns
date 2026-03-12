import asyncio
from importlib.resources import files

ASSETS_DIR = files("ns_admin") / "assets"
INTROSPECTION_DIR = files("ns_admin") / "introspection"

# sudo journalctl --output=cat --output-fields=SYSLOG_IDENTIFIER --since "12 hours ago" | sort -u


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
