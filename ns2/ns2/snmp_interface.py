

from dataclasses import asdict
from dbus_next.service import ServiceInterface, method

from ns2.snmp import *

class SnmpInterface(ServiceInterface):
    def __init__(self, name):
        super().__init__(name)
        self.bus = None

    @method()
    async def Reset(self):
        await ResetSnmpd(self.bus)

# ====================================================================
# V3 USERS
# ====================================================================
    @method()
    async def CreateV3User(self, v3User: 'a{ss}'):
        await AddV3User(self.bus, V3User.from_dict(v3User))

    @method()
    async def GetV3UserByUsername(self, username :'s') -> 'a{ss}':
        return asdict(await ReadV3UserByUsername(username))

    @method()
    async def GetV3Users(self) -> 'aa{ss}':
        return [asdict(u) for u in (await ReadV3Users())]

    @method()
    async def ModifyV3User(self, initUser: 'a{ss}', finalUser: 'a{ss}'):
        await EditV3User(self.bus, V3User.from_dict(initUser), V3User.from_dict(finalUser))

    @method()
    async def RemoveV3User(self, v3User: 'a{ss}'):
        await DeleteV3User(self.bus, V3User.from_dict(v3User))
    
# ====================================================================
# V2 USERS
# ====================================================================

    @method()
    async def CreateV2User(self, v2User: 'a{ss}'):
        await AddV2User(self.bus, V2User.from_dict(v2User))

    @method()
    async def GetV2UserByCommunity(self, community :'s') -> 'a{ss}':
        return asdict(await ReadV2UserByCommunity(community))

    @method()
    async def GetV2Users(self) -> 'aa{ss}':
        return [asdict(u) for u in await ReadV2Users()]

    @method()
    async def ModifyV2User(self, editUser: 'a{ss}'):
        await EditV2User(self.bus, V2User.from_dict(editUser))

    @method()
    async def RemoveV2User(self, v2User: 'a{ss}'):
        await DeleteV2User(self.bus, V2User.from_dict(v2User))

# ====================================================================
# 
# ====================================================================