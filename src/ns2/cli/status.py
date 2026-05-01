import asyncio
from ns2.cli.main import status_cli
from ns2.lib.ns_socket import read_write_socket, listen_to


@status_cli.command()
def enable(start: int, end: int):
    for i in range(start, end + 1):
        asyncio.run(read_write_socket(f"$NVS{i}={int(1)}"))


@status_cli.command()
def disable(start: int, end: int):
    for i in range(start, end + 1):
        asyncio.run(read_write_socket(f"$NVS{i}={int(0)}"))


@status_cli.command()
def listen(path: str = "/var/lib/ns/ns-serial-mux.sock"):
    asyncio.run(listen_to(path))


# @cli.command()
# def ser():
#    cmd = typer.prompt("Serial command")
#    if cmd:
#        rsp = asyncio.run(read_write_socket(cmd))
#
#        if rsp:
#            print(rsp.strip("\r\n"))
#        else:
#            print("no rsp or no cmd")
