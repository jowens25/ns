package lib

import (
	"fmt"
	"os/user"

	"log"

	"github.com/godbus/dbus/v5"
)

type DbusCall struct {
	Destination string          `json:"Destination" binding:"required"` // object
	Path        dbus.ObjectPath `json:"Path" binding:"required"`        // object
	Method      string          `json:"Method" binding:"required"`      // call
	Args        []any           `json:"Args"`                           // call
}

func Call(destination string, path dbus.ObjectPath, method string, args []any) (any, error) {
	conn, err := dbus.SystemBus()
	if err != nil {
		log.Println(err.Error())
	}

	var result any

	obj := conn.Object(destination, path)

	call := obj.Call(method, 0, args...)

	err = call.Store(&result)
	if err != nil {
		return nil, err
	}
	return result, nil

}

func MakeDbusCall(conn *dbus.Conn, call DbusCall) (any, any, error) {

	var result any

	obj := conn.Object(call.Destination, call.Path)

	dbuscall := obj.Call(call.Method, 0, call.Args...)
	fmt.Println("dbuscall: ", dbuscall)

	err := dbuscall.Store(&result)

	if err != nil {
		return nil, nil, err
	}
	return dbuscall.Body[0], result, nil

}

func GetUserInfoFromSender(conn *dbus.Conn, sender dbus.Sender) (*user.User, error) {

	var response map[string]dbus.Variant

	obj := conn.Object("org.freedesktop.DBus", "/org/freedesktop/DBus")
	err := obj.Call("org.freedesktop.DBus.GetConnectionCredentials", 0, sender).Store(&response)
	if err != nil {
		return nil, err
	}

	uid := response["UnixUserID"].Value().(uint32)

	u, err := user.LookupId(fmt.Sprintf("%d", uid))
	if err != nil {
		return nil, err
	}

	return u, nil

}
