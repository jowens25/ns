import pam
from dbus_next.service import ServiceInterface, method


class PamInterface(ServiceInterface):
    def __init__(self, name):
        super().__init__(name)

    @method()
    def Authenticate(self, username: 's', password: 's') -> 'b':
        p = pam.pam()
        if p.authenticate(username, password, print_failure_messages=True):
            print("authentication successful")
            return True
        else:
            print("authentication failed")

            return False

