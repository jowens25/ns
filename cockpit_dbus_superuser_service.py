import asyncio
from dataclasses import asdict
from dbus_next.service import ServiceInterface, method, dbus_property, signal

class Superuser(ServiceInterface):
    def __init__(self, name):
        super().__init__(name)
        self._current = 'none'
        self._pending = None

    @dbus_property()
    def Current(self) -> 's':
        return self._current

    @Current.setter
    def Current(self, val: 's'):
        self._current = val

    @signal()
    def Prompt(self, message, prompt, default, echo, error):
        pass

    @method()
    async def Start(self, name: 's'):
        self._current = 'init'
        self.emit_properties_changed({'Current': self._current})

        self._pending = asyncio.get_running_loop().create_future()
        self.Prompt('', 'Password', '', False, '')

        reply = await self._pending
        if reply:
            self._current = 'unlocked'
        else:
            self._current = 'none'

        self.emit_properties_changed({'Current': self._current})

    @method()
    def Answer(self, reply: 's'):
        if self._pending:
            self._pending.set_result(reply)

    @method()
    def Stop(self):
        self._current = 'none'
        self.emit_properties_changed({'Current': self._current})
