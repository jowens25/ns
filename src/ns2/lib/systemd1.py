import asyncio
from dbus_next.signature import Variant
from ns2.lib.bridge import BridgeCall, GetBridge
from ns2.utils import log


async def ListUnits() -> str:

    rsp = await BridgeCall(
        destination="org.freedesktop.systemd1",
        path="/org/freedesktop/systemd1",
        interface="org.freedesktop.systemd1.Manager",
        member="ListUnits",
        signature="",
        body=[],
    )

    return rsp.body[0]


async def GetSystemdProxy():
    bridge = GetBridge()
    introspection = await bridge.introspect(
        "org.freedesktop.systemd1", "/org/freedesktop/systemd1"
    )
    obj = bridge.get_proxy_object(
        "org.freedesktop.systemd1", "/org/freedesktop/systemd1", introspection
    )
    return obj.get_interface("org.freedesktop.systemd1.Manager")


async def SystemdStart(service: str):
    async def on_job_removed(id, job_path, unit, result):
        job_dict = {
            "id": id,
            "job_path": job_path,
            "unit": unit,
            "method": "start",
            "result": result,
        }
        if job_path == job and not job_future.done():
            if result != "done":
                job_future.set_exception(Exception(f"Job failed: {result}"))
            else:
                job_future.set_result(job_dict)

    job_future = asyncio.Future()
    systemd = await GetSystemdProxy()
    systemd.on_job_removed(on_job_removed)
    try:
        job = await systemd.call_start_unit(service, "replace")
        log.info(await job_future)

    finally:
        systemd.off_job_removed(on_job_removed)


async def SystemdStop(service: str):
    async def on_job_removed(id, job_path, unit, result):
        job_dict = {
            "id": id,
            "job_path": job_path,
            "unit": unit,
            "method": "stop",
            "result": result,
        }
        if job_path == job and not job_future.done():
            if result != "done":
                job_future.set_exception(Exception(f"Job failed: {result}"))
            else:
                job_future.set_result(job_dict)

    #
    job_future = asyncio.Future()
    systemd = await GetSystemdProxy()
    systemd.on_job_removed(on_job_removed)
    try:
        job = await systemd.call_stop_unit(service, "replace")
        log.info(await job_future)
    #
    finally:
        systemd.off_job_removed(on_job_removed)


#
#
async def SystemdRestart(service: str):
    async def on_job_removed(id, job_path, unit, result):
        job_dict = {
            "id": id,
            "job_path": job_path,
            "unit": unit,
            "method": "restart",
            "result": result,
        }
        if job_path == job and not job_future.done():
            if result != "done":
                job_future.set_exception(Exception(f"Job failed: {result}"))
            else:
                job_future.set_result(job_dict)

    #
    job_future = asyncio.Future()
    systemd = await GetSystemdProxy()
    systemd.on_job_removed(on_job_removed)
    try:
        job = await systemd.call_restart_unit(service, "replace")
        log.info(await job_future)
    #
    finally:
        systemd.off_job_removed(on_job_removed)


#
#
async def getUnitPath(service: str) -> str:
    rsp = await BridgeCall(
        destination="org.freedesktop.systemd1",
        path="/org/freedesktop/systemd1",
        interface="org.freedesktop.systemd1.Manager",
        member="GetUnit",
        signature="s",
        body=[service],
    )

    unitPath = rsp.body[0]

    return unitPath


async def getUnitProperties(unitPath: str) -> dict:

    rsp = await BridgeCall(
        destination="org.freedesktop.systemd1",
        path=unitPath,
        interface="org.freedesktop.DBus.Properties",
        member="GetAll",
        signature="s",
        body=["org.freedesktop.systemd1.Unit"],
    )
    unitProps = rsp.body[0]
    return unitProps


#


async def GetServiceState(service: str) -> str:
    path = await getUnitPath(service)
    props = await getUnitProperties(path)
    return props.get("ActiveState", Variant("s", "StateNotFound")).value


async def isActive(service: str) -> bool:
    state = await GetServiceState(service)
    log.info(f"{service} is active: {state}")
    if state == "active":
        return True
    else:
        return False
