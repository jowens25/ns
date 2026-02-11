

import asyncio
from dbus_next.signature import Variant
from dbus_next.aio.proxy_object import ProxyInterface
from dbus_next.aio import MessageBus as MessageBus
from dbus_next.glib import MessageBus as SyncBus
from dbus_next import Message, MessageType




async def AddMatch(bus: MessageBus, sender: str, interface: str, member: str):
    await bus.call(
        Message(
            destination='org.freedesktop.DBus',
            path='/org/freedesktop/DBus',
            interface='org.freedesktop.DBus',
            member='AddMatch',
            signature='s',
            body=[f"type='signal',sender={sender},interface={interface},member={member}"]
        )
    )
    

async def RemoveMatch(bus: MessageBus, sender: str, interface: str, member: str):
    await bus.call(
        Message(
            destination='org.freedesktop.DBus',
            path='/org/freedesktop/DBus',
            interface='org.freedesktop.DBus',
            member='RemoveMatch',
            signature='s',
            body=[f"type='signal',sender={sender},interface={interface},member={member}"]
        )
    )
    


async def Subscribe(bus: MessageBus):
    await bus.call(
    Message(
            destination='org.freedesktop.systemd1',
            path='/org/freedesktop/systemd1',
            interface='org.freedesktop.systemd1.Manager',
            member='Subscribe',
            signature='',
            body=[]
        )
    )
    return None

async def startUnit(bus: MessageBus, service: str) -> str:
    rsp = await bus.call(
    Message(
            destination='org.freedesktop.systemd1',
            path='/org/freedesktop/systemd1',
            interface='org.freedesktop.systemd1.Manager',
            member='StartUnit',
            signature='ss',
            body=[service, 'replace']
        )
    )
    return rsp.body[0]

async def stopUnit(bus: MessageBus, service: str) -> str:
    rsp = await bus.call(
    Message(
            destination='org.freedesktop.systemd1',
            path='/org/freedesktop/systemd1',
            interface='org.freedesktop.systemd1.Manager',
            member='StopUnit',
            signature='ss',
            body=[service, 'replace']
        )
    )
    return rsp.body[0]


async def restartUnit(bus: MessageBus, service: str) -> str:
    rsp = await bus.call(
    Message(
            destination='org.freedesktop.systemd1',
            path='/org/freedesktop/systemd1',
            interface='org.freedesktop.systemd1.Manager',
            member='RestartUnit',
            signature='ss',
            body=[service, 'replace']
        )
    )
    return rsp.body[0]


    
async def wait_for_job_removed(bus: SyncBus, job_path: str):
    job_future = asyncio.Future()
    
    print("looking for: ", job_path)
    
    def handler(msg):
        print("msg: ", msg)
        if (msg.message_type == MessageType.SIGNAL and
            msg.interface == 'org.freedesktop.systemd1.Manager' and
            msg.member == 'JobRemoved'):
            
            _, path, _, result = msg.body
            if path == job_path and not job_future.done():
                if result == 'done':
                    job_future.set_result(True)
                else:
                    job_future.set_exception(
                        Exception(f"Job failed: {result}")
                    )

    bus.add_message_handler(handler)

    try:
        return await asyncio.wait_for(job_future, 2.0)
    finally:
        bus.remove_message_handler(handler)


async def systemd_start(bus: MessageBus, service: str):
    await Subscribe(bus)
    await AddMatch(bus, 'org.freedesktop.systemd1',
                   'org.freedesktop.systemd1.Manager', 'JobRemoved')

    try:
        job = await startUnit(bus, service)
        return await wait_for_job_removed(bus, job)
    finally:
        await RemoveMatch(bus, 'org.freedesktop.systemd1',
                          'org.freedesktop.systemd1.Manager', 'JobRemoved')


#async def systemd_start(bus: MessageBus, service: str):
#    async def on_job_removed(id, job_path, unit, result):
#        job_dict = {"id":id,
#                    "job_path":job_path,
#                    "unit":unit,
#                    "method": "start",
#
#                    "result":result}
#        if job_path == job and not job_future.done():
#            if result != 'done':
#                job_future.set_exception(Exception(f"Job failed: {result}"))
#            else:
#                job_future.set_result(job_dict)
#    
#    job_future = asyncio.Future()
#    systemd = await getSystemdManager(bus)
#    systemd.on_job_removed(on_job_removed)
#    try: 
#        job = await systemd.call_start_unit(service, 'replace')
#        print(await job_future)
#        
#    finally: 
#        systemd.off_job_removed(on_job_removed)
#        
#        
#        
        
        
        
        
        
        
        
async def systemd_stop(bus: MessageBus, service: str):
    async def on_job_removed(id, job_path, unit, result):
        job_dict = {"id":id,
                    "job_path":job_path,
                    "unit":unit,
                    "method": "stop",
                    "result":result}
        if job_path == job and not job_future.done():
            if result != 'done':
                job_future.set_exception(Exception(f"Job failed: {result}"))
            else:
                job_future.set_result(job_dict)
    
    job_future = asyncio.Future()
    systemd = await getSystemdManager(bus)
    systemd.on_job_removed(on_job_removed)
    try: 
        job = await systemd.call_stop_unit(service, 'replace')
        print(await job_future)
        
    finally: 
        systemd.off_job_removed(on_job_removed)
        
        

async def systemd_restart(bus: MessageBus, service: str):
    async def on_job_removed(id, job_path, unit, result):
        job_dict = {"id":id,
                    "job_path":job_path,
                    "unit":unit,
                    "method": "restart",
                    "result":result}
        if job_path == job and not job_future.done():
            if result != 'done':
                job_future.set_exception(Exception(f"Job failed: {result}"))
            else:
                job_future.set_result(job_dict)
    
    job_future = asyncio.Future()
    systemd = await getSystemdManager(bus)
    systemd.on_job_removed(on_job_removed)
    try: 
        job = await systemd.call_restart_unit(service, 'replace')
        print(await job_future)
        
    finally: 
        systemd.off_job_removed(on_job_removed)




async def getUnitPath(bus: MessageBus, service: str) -> str:
    rsp = await bus.call(
        Message(
            destination='org.freedesktop.systemd1',
            path='/org/freedesktop/systemd1',
            interface='org.freedesktop.systemd1.Manager',
            member='GetUnit',
            signature='s',
            body=[service]
        )
    )
    
    unitPath = rsp.body[0]
    
    return unitPath



async def getUnitProperties(bus: MessageBus, unitPath: str) -> dict:
        
    rsp = await bus.call(
    Message(
        destination='org.freedesktop.systemd1',
        path=unitPath,
        interface='org.freedesktop.DBus.Properties',
        member='GetAll',
        signature='s',
        body=['org.freedesktop.systemd1.Unit']
        )
    )
    unitProps = rsp.body[0]
    return unitProps
    
    
async def getServiceState(bus: MessageBus, service: str) -> str:
    path = await getUnitPath(bus, service)
    props = await getUnitProperties(bus, path)
    return props.get("ActiveState", Variant('s', 'StateNotFound')).value



async def isActive(bus: MessageBus, service: str) -> bool:
    state = await getServiceState(bus, service)
    print(f'{service} is active: {state}')
    if state == 'active':
        return True
    else:
        return False