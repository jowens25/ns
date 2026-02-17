
from pprint import pprint
from dbus_next.aio import MessageBus

import asyncio
import time
from dbus_next.constants import BusType

from ns_socket import sendCommands

from ntl import NtpServerProperties

async def test_snmp_client():
    
    #with open('configs/PtpGmNtpServer.ucm') as f:
    #    content = f.read()
    #await WriteConfig(content)
    
    cmds = {}
    
    for propName, i in NtpServerProperties.items():
        cmds[propName] = f'$GPNTL,22,{i},?'
        
    #for i in range(len(NtpServerProperties)):
    #    cmds[str(i)] = f'$BAUDNV'
        

    start = time.time_ns()
    print(await sendCommands(cmds, True))
    print((time.time_ns()-start)/(10**9))


    #def rx_callback(msg):
    #    print(msg)
        
    #sock.on_rx(rx_callback)

    #while True:
    #    await asyncio.sleep(0.1)

    #await asyncio.wait()


if __name__ == "__main__":
    asyncio.run(test_snmp_client())