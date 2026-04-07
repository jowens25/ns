import os
import socket
import time
from dataclasses import dataclass, asdict
import asyncio
from asyncio import StreamWriter, StreamReader
from nicegui import Event, app

from collections import deque
socket_received = Event()

socket_writer = None
socket_reader = None

async def socket_setup():
    global socket_reader, socket_writer
    try: 
        socket_reader, socket_writer = await asyncio.open_unix_connection("/tmp/serial.sock")
        print("SOCKET OPENED")
        await read_socket()
    
    except FileNotFoundError:
        print("SOCKET NOT AVAILABLE")
        socket_received.emit("Socket Not Available")

        #raise 

    except asyncio.CancelledError:
        print("SOCKET LISTENER CANCELLED")
        raise
        
    finally:
        await socket_cleanup()
        
async def socket_cleanup():
    global socket_writer

    print("SOCKET LISTENER CLOSED")
    if socket_writer:
        socket_writer.close()
        await socket_writer.wait_closed()


        
        
async def read_socket():
    global socket_reader
    while True:
        data = await socket_reader.read(128)
        if data:
            record_data(data)
            # Emit event with the data - any subscribed UI can receive it
            socket_received.emit(data.decode('utf-8', errors='ignore'))
        else:
            # Socket closed by remote end
            break
        
        #get_data()



def record_data(data):
    latest = data.decode('utf-8', errors='ignore')
    with open("data.txt", "a") as f:
        f.writelines(latest)
    
    with open("data.txt", "r+") as f:
        lines = f.readlines()
        n = len(lines)
        if n >= 10000:
            lines = lines[n-10000:]
            f.seek(0)       # go to start of file
            f.truncate() 
            f.writelines(lines)




async def write_socket(command: str):
    global socket_writer
    command = command+"\r\n"
    socket_writer.write(command.encode())
    await socket_writer.drain()



def ReadWriteSocket(command: str) -> str:
    command = command + "\r\n"
    
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/tmp/serial.sock")
        sock.settimeout(4.0)  # 4 second timeout
        
        try:
            sock.sendall(command.encode('utf-8'))
            sock_file = sock.makefile('r')
            
            while True:
                line = sock_file.readline()
                    
                if any(marker in line for marker in ["$ER", "$RR", "$WR", "$GPNTL"]):
                    return line, None
            
        finally:
            sock.close()
            
    except socket.timeout:
        return "timeout"
    except ConnectionRefusedError as e:
        print("socket error?")
        return "port open error"
    except Exception as e:
        print(e)
        return "port write error"





def ReadNtlProperty(module: int, property :int) -> list[str]:
    return ReadWriteSocket(f"$GPNTL,{module},{property},?")

def WriteNtlProperty(module: int, property :int, value :str):
    return ReadWriteSocket(f"$GPNTL,{module},{property},{value}")

def ParseNtlResponse(response :str)->str:
    fields = response.split(",")
    if len(fields) == 4:
        module = fields[1]
        property = fields[2]
        value = fields[3]
        return value
              


def LoadConfig(file_name: str):

    print("LOADING CONFIG...")
    
    try:
        with open(file_name, 'r') as f:
            data = f.read()
    except Exception as err:
        print(f"file err: {err}")
        return
    
    for line in data.split('\n'):
        # Skip comments
        if "--" in line:
            continue
        
        # Process $WC commands
        if "$WC" in line:
            line = line.strip()  # Remove whitespace and newlines
            
            rsp, err = ReadWriteSocket(line)
            
            if rsp.startswith("$ER"):
                print("config load err")
                return
            
            if err is not None:
                print("config error")
                return
            
            print(rsp)