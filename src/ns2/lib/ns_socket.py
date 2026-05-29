import asyncio
from nicegui import Event


from ns2.utils import log

socket_path = "/var/lib/ns/ns-serial-mux.sock"

socket_receive = Event()

socket_open = False


async def main(max_string: int):
    _, writer = await asyncio.open_unix_connection(socket_path)

    for i in range(max_string + 1):
        cmd = f"$NVS{i}=1\r\n"
        log.info("sending: ", cmd)
        writer.write(cmd.encode())
        await writer.drain()

    writer.close()
    await writer.wait_closed()


def set_status_string(status, num):
    return f"$NVS{int(num)}={int(status)}"


async def listen_to(path):

    socket_path = path
    reader, _ = await asyncio.open_unix_connection(socket_path)
    while True:
        line = await reader.readline()

        if line:
            log.info(line.decode("utf-8", errors="ignore").strip("\r\n"))


async def read_socket(reader, cmd, timeout=1):

    rsps = []

    try:
        async with asyncio.timeout(timeout):
            while True:
                line = await reader.readline()

                if not line:
                    break

                line = line.decode("utf-8")

                if line.startswith(cmd):
                    rsps.append(line)
                    break

    except TimeoutError:

        pass

    return rsps


async def read_write_socket(cmd: str) -> str:

    socket_path = "/var/lib/ns/ns-serial-mux.sock"
    reader, writer = await asyncio.open_unix_connection(socket_path)

    read_task = asyncio.create_task(read_socket(reader, cmd))

    writer.write((cmd + "\r\n").encode())
    await writer.drain()

    responses = await read_task

    writer.close()

    await writer.wait_closed()

    return "".join(responses)


async def socket_stream():
    global socket_open
    try:
        reader, writer = await asyncio.open_unix_connection(socket_path)
        log.info("SOCKET OPENED")
        socket_open = True
        while True:
            line = (await reader.readline()).decode("utf-8", errors="ignore")
            if line:
                # yield line
                socket_receive.emit(line)
                # record_line(line)
            else:
                break
    except FileNotFoundError:
        log.info("SOCKET NOT AVAILABLE")
        # self.socket_received.emit("Socket Not Available")
        socket_open = False
        raise
    except asyncio.CancelledError:
        log.info("SOCKET LISTENER CANCELLED")
        socket_open = False
        if writer:
            writer.close()
            await writer.wait_closed()
        raise
    finally:
        log.info("SOCKET LISTENER CLOSED")
        socket_open = False
        if writer:
            writer.close()
            await writer.wait_closed()


async def sendCommands(commands: dict, get_responses: bool = False) -> list[str]:
    reader, writer = await asyncio.open_unix_connection(socket_path)
    responses = {}
    for name, command in commands.items():
        log.info("sending: ", command)
        command = command + "\r\n"
        writer.write(command.encode())
        await writer.drain()
        # log.info("finsihed drain")
        if get_responses:
            try:
                # await asyncio.wait_for(rx, 2.0)

                while True:
                    # log.info("awaiting for response")
                    line = (await reader.readline()).decode("utf-8", errors="ignore")
                    if line:
                        if any(
                            line.startswith(marker)
                            for marker in ["$ER", "$RR", "$WR", "$GPNTL", "$BAUD"]
                        ):
                            log.info(f"got: {line}")
                            responses[name] = ParseNtlResponse(line)
                            # responses.append(line)
                            break
                            # return line
                            # rx.set()

                    # await rx.wait()

            except TimeoutError:
                responses[name] = "TimeoutError: no response?"

    writer.close()
    await writer.wait_closed()

    return responses


def record_line(line):
    with open("data.txt", "a") as f:
        f.writelines(line)

    with open("data.txt", "r+") as f:
        lines = f.readlines()
        n = len(lines)
        if n >= 10000:
            lines = lines[n - 10000 :]
            f.seek(0)  # go to start of file
            f.truncate()
            f.writelines(lines)


async def ReadNtlProperties(module: int, props: dict):
    cmds = {}

    for propName, propInt in props.items():
        cmds[propName] = f"$GPNTL,{module},{propInt},?"

    return await sendCommands(cmds, True)
    # for r in rsp:
    #    a["module"] = ParseNtlResponse(r)
    # return a


async def ReadNtlProperty(module: int, property: int) -> list[str]:
    rsp = await sendCommands([f"$GPNTL,{module},{property},?"], True)

    return ParseNtlResponse(rsp)


async def WriteNtlProperty(module: int, property: int, value: str):
    return await sendCommands([f"$GPNTL,{module},{property},{value}"], True)


def ParseNtlResponse(response: str) -> str:
    fields = response.split(",")
    if len(fields) == 4:
        # module = fields[1]
        # property = fields[2]
        value = fields[3]
        return value.strip("\r\n")


async def WriteConfig(content: str):
    commands = {
        i: line for i, line in enumerate(content.splitlines()) if line.startswith("$WC")
    }
    await sendCommands(commands)
