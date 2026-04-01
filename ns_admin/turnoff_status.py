import asyncio
import sys

socket_path = "/var/lib/ns/ns-serial-mux.sock"


async def main(max_string: int):
    reader, writer = await asyncio.open_unix_connection(socket_path)

    for i in range(max_string + 1):
        cmd = f"$NVS{i}=1\r\n"
        print("sending: ", cmd)
        writer.write(cmd.encode())
        await writer.drain()

    writer.close()
    await writer.wait_closed()


asyncio.run(main(int(sys.argv[1])))
