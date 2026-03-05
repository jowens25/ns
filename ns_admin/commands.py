

import asyncio
import subprocess


#def runCmd(args: list[str]) -> tuple[str, str]:
#    print(f"running: {args}")
#    result = subprocess.run(args, capture_output=True, text=True)
#    return result.stdout


async def runCmd(args: list[str]) -> str:
    print(f"running: {args}")
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode()


async def runAsyncCmd(args: list[str]) -> str:
    print(f"running: {args}")
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode()