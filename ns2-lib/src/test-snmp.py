#!/usr/bin/env python3

import asyncio
import sys
from pysnmp.hlapi import *
from pysnmp.hlapi.v3arch.asyncio import *


async def snmp_set_nsCommand(host: str, community: str, command:str):
    
    nsCommand = ".1.3.6.1.4.1.9183.1.1.9.1.0"

    error_indication, error_status, error_index, var_binds = await set_cmd(
            SnmpEngine(),
            CommunityData(community),  # SNMPv2
            await UdpTransportTarget.create((host, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(nsCommand), OctetString(command)),
        )
    
    for var_bind in var_binds:
        oid, value = var_bind
        print(f"\nOID: {oid.prettyPrint()}")
        print(f"Value: {value.prettyPrint()}")
        return value.prettyPrint(), None, None, None

async def snmp_get_nsResult(host: str, community: str):
    
    nsResult = ".1.3.6.1.4.1.9183.1.1.9.2.0"

    error_indication, error_status, error_index, var_binds = await get_cmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1),  # SNMPv2
            await UdpTransportTarget.create((host, 161)),
            ContextData(),
            ObjectType(
                ObjectIdentity(nsResult)
            )
        )
    
    
    for var_bind in var_binds:
        oid, value = var_bind
        print(f"\nOID: {oid.prettyPrint()}")
        print(f"Value: {value.prettyPrint()}")
        return value.prettyPrint(), None, None, None


async def main():
    
    host = "10.1.10.205"
    com = "novus"
    cmd = "$BAUDNV"


    await snmp_set_nsCommand(host=host, community=com, command=cmd)
    
    await snmp_get_nsResult(host=host, community=com)
    
    
        
asyncio.run(main())