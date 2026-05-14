package lib

import (
	"fmt"
	"os"

	"github.com/godbus/dbus/v5"
)

//
//	var s any
//
//	obj := conn.Object("org.freedesktop.DBus", "/org/freedesktop/DBus")
//	err = obj.Call("org.freedesktop.DBus.GetConnectionUnixUser", 0, ugh_try_this).Store(&s)
//	if err != nil {
//		fmt.Println("Failed to call")
//		os.Exit(1)
//	}
//
//	fmt.Println(s)
//
//	u, _ := user.LookupId(fmt.Sprintf("%d", s))
//
//	fmt.Println(u)
//
//	return conn

func LookUpUserBasedOnConnection(sender dbus.Sender) {

	var s any

	conn, _ := dbus.SystemBus()

	obj := conn.Object("org.freedesktop.DBus", "/org/freedesktop/DBus")
	err := obj.Call("org.freedesktop.DBus.GetConnectionUnixUser", 0, sender).Store(&s)
	if err != nil {
		fmt.Println("Failed to call")
		os.Exit(1)
	}

	fmt.Println(s)

	fmt.Printf("actions available for: %d\n", s)
}
