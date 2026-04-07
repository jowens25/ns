import sys

from ns_admin.ui.main_page import ui_main

from ns_admin.api.main import dbus_main

if len(sys.argv) > 1:
    if sys.argv[1] == "ui":
        if len(sys.argv) == 3:
            debug_mode = sys.argv[2]
        else:
            debug_mode = "production"
        ui_main(debug_mode)
    elif sys.argv[1] == "dbus":
        dbus_main()
    else:
        print("arg invalid")

else:
    print("Please run ns2 ui or ns2 dbus")
