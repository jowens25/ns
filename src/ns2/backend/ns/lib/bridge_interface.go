package lib

import (
	"fmt"

	"github.com/godbus/dbus/v5"
)

// implements the com.novus.ns.bridge interface com.novus.ns.bridge.Call
type BridgeInterface struct{}

func (b *BridgeInterface) InitSession(username string) (map[string]string, *dbus.Error) {

	port := ":8080"
	handle := "/" + username

	pid := CallMakeBridge(username) // calls -> InitServerProcess()

	return map[string]string{
		"pid":  fmt.Sprintf("%d", pid),
		"path": fmt.Sprintf("ws://127.0.0.1%s%s", port, handle),
	}, nil

	//return result, nil
}

func (b *BridgeInterface) EndSession(pid int) *dbus.Error {
	CallEndBridge(pid)
	return nil
}
