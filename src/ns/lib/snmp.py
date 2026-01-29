
import os
import sys
from dataclasses import asdict, dataclass
from ns.lib.commands import runCmd
from typing import Optional
import aiofiles

from ns.lib.systemd import *

snmp_config_file = "/etc/snmp/snmpd.conf"
default_persistent_dir_path = "/var/lib/snmp"




USM_OID_MAP = {
    # Authentication Protocols (RFC 3414)
    "1.3.6.1.6.3.10.1.1.1": "NoAuth",
    ".1.3.6.1.6.3.10.1.1.2": "MD5", 
    ".1.3.6.1.6.3.10.1.1.3": "SHA",
    "1.3.6.1.6.3.10.1.1.4": "HMAC-SHA2-224",
    "1.3.6.1.6.3.10.1.1.5": "HMAC-SHA2-256",
    
    # Privacy Protocols (RFC 3414 + 3826)
    "1.3.6.1.6.3.10.1.2.1": "NoPriv",
    ".1.3.6.1.6.3.10.1.2.2": "DES",
    ".1.3.6.1.6.3.10.1.2.4": "AES",
    "1.3.6.1.6.3.10.1.2.5": "AES-192", 
    "1.3.6.1.6.3.10.1.2.6": "AES-256"
}


@dataclass
class Group:
    Permissions: Optional[str] = None
    Version: Optional[str] = None
    SecName: Optional[str] = None

@dataclass
class V3User:
    UserName: Optional[str] = ''
    Version: Optional[str] = 'usm'
    AuthType: Optional[str] = 'SHA'
    AuthPassphrase: Optional[str] = ''
    PrivType: Optional[str] = 'AES'
    PrivPassphrase: Optional[str] = ''
    Permissions: Optional[str] = 'rwprivgroup'
    


    def from_dict(userDict :dict):
            user = V3User(
                UserName = userDict.get('UserName'),
                Version = userDict.get('Version'),
                AuthType = userDict.get('AuthType'),
                AuthPassphrase = userDict.get('AuthPassphrase'),
                PrivType = userDict.get('PrivType'),
                PrivPassphrase = userDict.get('PrivPassphrase'),
                Permissions = userDict.get('Permissions')
            )
            return user

@dataclass
class V2User:
    Community:Optional[str] = ''
    Version:Optional[str] = ''
    Permissions:Optional[str] = ''
    Source:Optional[str] = ''
    SecName:Optional[str] = ''

    def from_dict(userDict :dict):
        user = V2User(
            Community = userDict.get('Community'),
            Version = userDict.get('Version'),
            Permissions = userDict.get('Permissions'),
            Source = userDict.get('Source'),
            SecName = userDict.get('SecName')
        )
        return user





# ====================================================================
# SNMP Files and Directories
# ====================================================================        
async def _readSnmpGroupsFromFile() -> list[Group]:
    groups = []
    async with aiofiles.open(snmp_config_file, "r") as f:        
        async for line in f:
            line = line.strip("\n")
            if line.startswith("group"):
                g = Group()
                fields = line.split(" ")
                if len(fields) == 4:
                    g.Permissions = fields[1]
                    g.Version = fields[2]
                    g.SecName = fields[3]
                    groups.append(g)
        pass #endfor  
    return groups

async def _readV2UsersFromFile() -> list[V2User]:
    v2s = []
    async with aiofiles.open(snmp_config_file, "r") as f:
        async for line in f:
            line = line.strip("\n")
            if line.startswith("com2sec"):
                v2 = V2User()
                fields = line.split(" ")
                if len(fields) == 4:
                    v2.SecName = fields[1]
                    v2.Source = fields[2]
                    v2.Community = fields[3]
                    v2s.append(v2)
        pass #endfor
    return v2s

async def _readV3UsersFromFile() -> list[V3User]:
    v3s = []
    try:
        async with aiofiles.open(await _getPersistentConfPath(), "r") as f:
            async for line in f:
                line = line.strip("\n")
                if line.startswith("usmUser"):
                    v3 = V3User()
                    fields = line.split(" ")
                    if len(fields) == 12:
                    
                        v3.UserName = fields[4].strip('"')

                        v3.AuthType = USM_OID_MAP.get(fields[7], f"Unknown")
                        #v3.AuthPassphrase = fields[3]
                        v3.PrivType = USM_OID_MAP.get(fields[9], f"Unknown")
                        #v3.PrivPassphrase = fields[5]
                        v3s.append(v3)
            pass # endfor
    except FileNotFoundError:
        return v3s
    return v3s

async def _writeV2User(user :V2User):
    '''add v2 user to file'''
    print("_writeV2User")
    lineCount = 0
    userIndex = -1
    groupIndex = -1

    comNumber = len(await ReadV2Users())

    async with aiofiles.open(snmp_config_file, "r") as f:
        content = await f.readlines()
    
        for line in content:
            line = line.strip("\n")
            if line.startswith("#com2sec"):
                userIndex = lineCount + 2
            if line.startswith("#group"):
                groupIndex = lineCount + 3
            lineCount = lineCount + 1
        pass # endfor 


    newUserLine = f"com2sec comuser_{comNumber} {user.Source} {user.Community}\n"
    newGroupLine = f"group {user.Permissions} {user.Version} comuser_{comNumber}\n"


    if userIndex < 0:
        content.append("#-------------------------------------------------------------------------------")
        content.append("#com2sec sec.name source community")
        content.append("#-------------------------------------------------------------------------------")
        content.append(newUserLine)
    else:
        content.insert(userIndex, newUserLine)

    if groupIndex < 0:
        content.append("#-------------------------------------------------------------------------------")
        content.append("#group  group name      sec.model  sec.name")
        content.append("#-------------------------------------------------------------------------------")
        content.append(newGroupLine)
    else:
        content.insert(groupIndex, newGroupLine)


    async with aiofiles.open(snmp_config_file, "w") as f:
        await f.writelines(content)
        #content = f.readlines()
    
async def _writeV3UserCreateDirective(user: V3User):
    '''add v3 user to file'''
    print("write v3 user")

    lineCount = 0
    createUserIndex = -1
    groupIndex = -1

    async with aiofiles.open(snmp_config_file, "r") as f:
        content = await f.readlines()
    
    for i, line in enumerate(content):
        line = line.strip("\n")
        if line.startswith("#createUser"):
            createUserIndex = lineCount + 2
        if line.startswith("#group"):
            groupIndex = lineCount + 3
        
        lineCount = lineCount + 1
    pass # endfor 

    newUserLine = f"createUser {user.UserName} {user.AuthType} {user.AuthPassphrase} {user.PrivType} {user.PrivPassphrase}\n"
    newGroupLine = f"group {user.Permissions} {user.Version} {user.UserName}\n"


    if createUserIndex < 0:
        content.append("#-------------------------------------------------------------------------------")
        content.append("#createUser username [MD5|SHA] [passphrase] [DES] [passphrase]")
        content.append("#-------------------------------------------------------------------------------")
        content.append(newUserLine)
    else:
        content.insert(createUserIndex, newUserLine)

    if groupIndex < 0:
        content.append("#-------------------------------------------------------------------------------")
        content.append("#group  group name      sec.model  sec.name")
        content.append("#-------------------------------------------------------------------------------")
        content.append(newGroupLine)
    else:
        content.insert(groupIndex, newGroupLine)


    async with aiofiles.open(snmp_config_file, "w") as f:
        await f.writelines(content)
    

async def _deleteV3UserFromStorage(user: V3User):
    '''delete v3 user from persistent storgage'''

    async with aiofiles.open(await _getPersistentConfPath()) as f:
        content = await f.readlines()

    for i, line in enumerate(content):
        if line.startswith("usmUser"):

            fields = line.split(" ")
            temp_auth_type = USM_OID_MAP.get(fields[7], f"Unknown")
            temp_priv_type = USM_OID_MAP.get(fields[9], f"Unknown")

            if user.UserName in line and temp_auth_type == user.AuthType and temp_priv_type == user.PrivType:
                content.remove(line)

    async with aiofiles.open(await _getPersistentConfPath(), "w") as f:
        await f.writelines(content)


async def _deleteV3UserCreateDirective(user: V3User):
    _props  = [user.UserName, user.AuthType, user.AuthPassphrase, user.PrivType, user.PrivPassphrase]

    async with aiofiles.open(snmp_config_file, "r") as f:
        content = await f.readlines()

    for i, line in enumerate(content):
        if line.startswith("createUser") and all(p in line for p in _props):
            content.remove(line)

    async with aiofiles.open(snmp_config_file, "w") as f:
        await f.writelines(content)
        

async def _deleteV3UserFromConfig(user: V3User):
    '''delete v3 user from /etc/snmp/snmpd.conf'''

    _props = [user.Permissions, user.Version, user.UserName]

    async with aiofiles.open(snmp_config_file, "r") as f:
        content = await f.readlines()
        
        for i, line in enumerate(content):
            if line.startswith("group") and all(p in line for p in _props):
                content.remove(line)

    async with aiofiles.open(snmp_config_file, "w") as f:
        await f.writelines(content)


async def _getPersistentDir() -> str:
    async with aiofiles.open(snmp_config_file, "r") as f:
        async for line in f:
            if line.startswith("persistentDir"): 
                fields = line.split(" ")
                if len(fields) == 2:
                    return fields[1].strip("\n")
    pass #endfor
    return None

async def _setPersistentDir(path):
    async with aiofiles.open(snmp_config_file, "r") as f:
        content = await f.readlines()
    
    for i, line in enumerate(content):
        if line.startswith("persistentDir"): 
            content[i] = f"persistentDir {path}\n"
            break
    async with aiofiles.open(snmp_config_file, "w") as f:
        await f.writelines(content)

        
async def _getPersistentConfPath() -> str:
    persistentDir = await _getPersistentDir()
    return os.path.join(persistentDir, "snmpd.conf")    
        
async def _deletePersistentDir():
    persistentDir = await _getPersistentDir()
    await runCmd(['rm', '-rf', persistentDir])
    
async def _overWriteWithDefaultSnmpConf():
    await runCmd(['cp', './configs/snmpd.conf', '/etc/snmp/snmpd.conf'])





    
async def ResetSnmpd(bus :MessageBus) -> str:
    # 1. Stop Snmp
    await systemd_stop(bus, 'snmpd.service')
    # 2. Remove Persistent Dir
    await _deletePersistentDir()
    # 3. Reset Main Config
    await _overWriteWithDefaultSnmpConf()
    # 4. Set Tmp Path for Persistent Dir
    await _setPersistentDir("/var/lib/tmp")
    # 5. Start Snmp
    await systemd_start(bus, 'snmpd.service')
    # 6. Stop Snmp
    await systemd_stop(bus, 'snmpd.service')
    # 7. Remove Temp Persistent Dir
    await _deletePersistentDir()
    # 8. Set Real Path for Persistent Dir
    await _setPersistentDir("/var/lib/snmp")
    # 9. Start Snmp
    await systemd_start(bus, 'snmpd.service')

    return "snmpd reset"



    

# ====================================================================
# V3 USERS
# ====================================================================
async def AddV3User(bus :MessageBus, user: V3User):
    '''add v3 user'''
    print('add v3 dude')
    await systemd_stop(bus, 'snmpd.service')
    await _writeV3UserCreateDirective(user)
    await systemd_start(bus, 'snmpd.service') # real user created
    await _deleteV3UserCreateDirective(user)

async def ReadV3UserByUsername(username: str) -> V3User:
    u :V3User
    for u in (await ReadV3Users()):
        if u.UserName == username:
            return u
    return None

async def ReadV3Users() -> list[V3User]:
    print('read v3 users')
    groups = await _readSnmpGroupsFromFile()
    v3s = await _readV3UsersFromFile()
    g: Group
    for g in groups:
        v3: V3User
        for v3 in v3s:
            if g.SecName == v3.UserName:
                print(g.SecName)
                v3.Permissions = g.Permissions
                v3.Version = g.Version
        pass #endfor
    pass #endfor
    print(v3s)
    return v3s

async def EditV3User(bus: MessageBus, inituser :V3User, finaluser: V3User):
    '''edit v3 user'''
    print("EditV3User")

    if not inituser:
        print("v3 USER NOT FOUND")
        #sys.exit()

    await systemd_stop(bus, 'snmpd.service')
    await _deleteV3UserFromStorage(inituser) # remove actual
    await _deleteV3UserFromConfig(inituser) # remove group
    await _writeV3UserCreateDirective(finaluser) # add grup and create
    await systemd_start(bus, 'snmpd.service')
    await _deleteV3UserCreateDirective(finaluser) # remove create dir

async def DeleteV3User(bus: MessageBus, user: V3User):
    await systemd_stop(bus, 'snmpd.service')
    await _deleteV3UserFromConfig(user)
    await _deleteV3UserFromStorage(user)
    await systemd_start(bus, 'snmpd.service')


# ====================================================================
# V2 USERS
# ====================================================================
async def AddV2User(bus: MessageBus, user: V2User):
    '''add v2 user'''
    print("add a v2 user")
    await systemd_stop(bus, 'snmpd.service')
    await _writeV2User(user)
    await systemd_start(bus, 'snmpd.service')

async def ReadV2UserByCommunity(community: str) -> V2User:
    u :V2User
    for u in await ReadV2Users():
        if u.Community == community:
            return u
    return None

async def ReadV2UserBySecurityName(secName: str) -> V2User:
    u :V2User
    for u in await ReadV2Users():
        if u.SecName == secName:
            return u
    return None


async def ReadV2Users() -> list[V2User]:
    groups = await _readSnmpGroupsFromFile()
    v2s = await _readV2UsersFromFile()
    g: Group
    for g in groups:
        v2: V2User
        for v2 in v2s:
            if g.SecName == v2.SecName:
                v2.SecName = g.SecName
                v2.Permissions = g.Permissions
                v2.Version = g.Version
        pass #endfor
    pass #endfor
    return v2s

async def EditV2User(bus : MessageBus, user: V2User):
    '''edit v2 user'''
    print("EditV2User")
    existingUser = await ReadV2UserBySecurityName(user.SecName)

    if not existingUser:
        print("USER NOT FOUND")
        sys.exit()

    await systemd_stop(bus, 'snmpd.service')
    await DeleteV2User(existingUser)
    await _writeV2User(user)
    await systemd_start(bus, 'snmpd.service')

async def DeleteV2User(bus : MessageBus, user: V2User):
    '''delete v2 user'''
    print('delete v2')
    
    await systemd_stop(bus, 'snmpd.service')
    
    _user = [ user.SecName, user.Source, user.Community]
    _group = [ user.Permissions, user.Version, user.SecName]

    async with aiofiles.open(snmp_config_file, "r") as f:
        content = await f.readlines()

    for line in content:
        if line.startswith("com2sec") and all(p in line for p in _user):
            content.remove(line)
        if line.startswith("group") and all(p in line for p in _group):
            content.remove(line)

    async with aiofiles.open(snmp_config_file, "w") as f:
        await f.writelines(content)
    
    
    await systemd_start(bus, 'snmpd.service')


# ====================================================================
# dbus
# ====================================================================

async def GetSnmp(bus: MessageBus):
    introspection = await bus.introspect('com.novus.ns', '/com/novus/ns')
    obj = bus.get_proxy_object('com.novus.ns', '/com/novus/ns', introspection)
    return obj.get_interface('com.novus.ns.snmp')


async def snmp_call(bus: MessageBus, member: str, signature:str, body):

    rsp = await bus.call(
        Message(
            destination='com.novus.ns',
            path='/com/novus/ns',
            interface='com.novus.ns.snmp',
            member=member,
            signature=signature,
            body=[body]
        )
    )
    
    if rsp.body:
        return rsp.body[0]