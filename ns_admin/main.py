
import sys

from ns_admin.ui import ui_main

from ns_admin.dbus import dbus_main

if len(sys.argv) > 1:
    if sys.argv[1] == "ui":
        ui_main()
    elif sys.argv[1] == "dbus":
        dbus_main()
    else:
        print("arg invalid")
        
else:
    print("Please run ns2 ui or ns2 dbus")
