from dataclasses import dataclass, asdict
import asyncio
from nicegui import Event, app

from dbus_next.service import ServiceInterface, method, signal
from dbus_next.aio import MessageBus


socket_receive = Event()
async def socket_stream():
    try: 
        reader, writer = await asyncio.open_unix_connection("/var/lib/ns/ns-serial-mux.sock")
        print("SOCKET OPENED")
        while True:
            line = (await reader.readline()).decode('utf-8', errors='ignore')
            if line:
                #yield line
                socket_receive.emit(line)
                record_line(line)
            else:
                break
    except FileNotFoundError:
        print("SOCKET NOT AVAILABLE")
        #self.socket_received.emit("Socket Not Available")
        raise 
    except asyncio.CancelledError:
        print("SOCKET LISTENER CANCELLED")
        if writer:
            writer.close()
            await writer.wait_closed()
        raise
    finally:
        print("SOCKET LISTENER CLOSED")
        if writer:
            writer.close()
            await writer.wait_closed()
        
 

async def sendCommands(commands: dict, get_responses :bool = False) -> list[str]:
    rx = asyncio.Event()
    reader, writer = await asyncio.open_unix_connection("/tmp/serial.sock")
    responses = {}
    for name, command in commands.items():
        print("sending: ", command)
        command = command+"\r\n"
        writer.write(command.encode())
        await writer.drain()
        #print("finsihed drain")
        if get_responses:
            try:
                #await asyncio.wait_for(rx, 2.0)

                while True:
                    #print("awaiting for response")
                    line = (await reader.readline()).decode('utf-8', errors='ignore')
                    if line:
                        if any(line.startswith(marker) for marker in ["$ER", "$RR", "$WR", "$GPNTL", "$BAUD"]):
                            print(f'got: {line}')
                            responses[name] = ParseNtlResponse(line)
                            #responses.append(line)
                            break
                            #return line
                            #rx.set()

                    #await rx.wait()

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
            lines = lines[n-10000:]
            f.seek(0)       # go to start of file
            f.truncate() 
            f.writelines(lines)




async def ReadNtlProperties(module :int, props: dict):
    cmds = {}
    
    for propName, propInt in props.items():
        cmds[propName] = f"$GPNTL,{module},{propInt},?"

    return await sendCommands(cmds, True)
    #for r in rsp:
    #    a["module"] = ParseNtlResponse(r)
    #return a

async def ReadNtlProperty(module: int, property :int) -> list[str]:
    rsp = await sendCommands([f"$GPNTL,{module},{property},?"], True)

    return ParseNtlResponse(rsp)


async def WriteNtlProperty(module: int, property :int, value :str):
    return await sendCommands([f"$GPNTL,{module},{property},{value}"], True)



def ParseNtlResponse(response :str)->str:
    fields = response.split(",")
    if len(fields) == 4:
        module = fields[1]
        property = fields[2]
        value = fields[3]
        return value.strip('\r\n')
              

async def WriteConfig(content :str):
    commands = {i: line for i, line in enumerate(content.splitlines()) if line.startswith('$WC')}
    await sendCommands(commands)




