package lib

import (
	"fmt"
	"log"
	"os/user"

	"github.com/godbus/dbus/v5"
)

func GetConnectionCredentials(conn *dbus.Conn) uint32 {
	var response map[string]dbus.Variant

	obj := conn.Object("org.freedesktop.DBus", "/org/freedesktop/DBus")
	err := obj.Call("org.freedesktop.DBus.GetConnectionCredentials", 0, conn.Names()[0]).Store(&response)
	if err != nil {
		log.Fatal("Failed to look up user")
	}

	return response["UnixUserID"].Value().(uint32)

}

func GetUserNameFromUid(uid uint32) string {

	u, err := user.LookupId(fmt.Sprintf("%d", uid))
	if err != nil {
		log.Fatalf("Could not find user with UID %s: %v", uid, err)
	}

	return u.Username
}

func GetUsernameFromConnection(conn *dbus.Conn) string {

	return GetUserNameFromUid(GetConnectionCredentials(conn))

}
