

import asyncio
from dbus_next.signature import Variant
from dbus_next.aio.proxy_object import ProxyInterface
from dbus_next.aio import MessageBus as MessageBus
from dbus_next.glib import MessageBus as SyncBus
from dbus_next import Message, MessageType

import time

async def getSystemdManager(bus: MessageBus) -> ProxyInterface:
    introspection = await bus.introspect('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
    obj = bus.get_proxy_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1', introspection)
    return obj.get_interface('org.freedesktop.systemd1.Manager')






async def systemd_start(bus: MessageBus, service: str):
    async def on_job_removed(id, job_path, unit, result):
        job_dict = {"id":id,
                    "job_path":job_path,
                    "unit":unit,
                    "method": "start",
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
        job = await systemd.call_start_unit(service, 'replace')
        print(await job_future)
        
    finally: 
        systemd.off_job_removed(on_job_removed)
        
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
    start = time.perf_counter()
    state = await getServiceState(bus, service)
    print(f'{service} is active: {state}')
    
    print("time: ", time.perf_counter()-start)
    if state == 'active':
        return True
    else:
        return False