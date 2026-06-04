package lib

import (
	"fmt"
	"log"
	"sync"

	"github.com/godbus/dbus/v5"
)

// implements the com.novus.ns.bridge interface com.novus.ns.bridge.Call

// Update your struct to hold the connection
type BridgeInterface struct {
	conn      *dbus.Conn
	props     map[string]any
	propsLock sync.RWMutex
}

// Add a constructor function
func NewBridgeInterface() *BridgeInterface {

	b := &BridgeInterface{
		props: make(map[string]any), // Initialize the map!
	}

	b.propsLock.Lock()
	b.props["pid"] = -1
	b.props["term"] = -1
	b.propsLock.Unlock()

	return b

}

//func FetchLogs(boot *int, since string, priority int, units []string) ([]string, error) {

func (b *BridgeInterface) GetLogs(since string, priority int, units []string) ([]string, *dbus.Error) {

	logs, err := FetchLogs(since, priority, units)

	if err != nil {
		return nil, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	return logs, nil
}

func (b *BridgeInterface) GetActiveUser(sender dbus.Sender) (string, *dbus.Error) {

	u, err := GetUserInfoFromSender(b.conn, sender)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}
	return u.Username, nil
}

func (b *BridgeInterface) Make(username string) (int, *dbus.Error) {

	b.propsLock.RLock()
	initPid, ok := b.props["pid"].(int)
	b.propsLock.RUnlock()

	if !ok {
		return -1, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{"pid type error"},
		}
	}

	if initPid > 0 {

		log.Println("closed existing bridge")

		err := callClose(initPid)
		if err != nil {
			return -1, &dbus.Error{
				Name: "org.freedesktop.DBus.Error",
				Body: []any{err.Error()},
			}
		}
	}

	pid, err := CallMakeBridge(username)

	if err != nil {

		return -1, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	b.propsLock.Lock()
	b.props["pid"] = pid
	b.propsLock.Unlock()

	if b.conn != nil {
		b.emitPropertiesChanged("com.novus.ns.bridge",
			map[string]dbus.Variant{
				"pid": dbus.MakeVariant(pid),
			},
			[]string{})
	}

	return pid, nil
}

func (b *BridgeInterface) Terminal(username string) (int, *dbus.Error) {

	b.propsLock.RLock()
	initPid, ok := b.props["term"].(int)
	b.propsLock.RUnlock()

	if !ok {
		return -1, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{"pid type error"},
		}
	}

	if initPid > 0 {

		log.Println("closed existing terminal")

		err := callClose(initPid)
		if err != nil {
			return -1, dbus.NewError(
				"org.freedesktop.DBus.Error",
				[]any{err.Error()},
			)
		}
	}

	pid, err := CallMakeTerminal(username)

	if err != nil {

		return -1, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	// Lock before writing to the map
	b.propsLock.Lock()
	b.props["term"] = pid
	b.propsLock.Unlock()

	if b.conn != nil {
		b.emitPropertiesChanged("com.novus.ns.bridge",
			map[string]dbus.Variant{
				"term": dbus.MakeVariant(pid),
			},
			[]string{})
	}

	return pid, nil
}

func (b *BridgeInterface) Close() (string, *dbus.Error) {
	b.propsLock.RLock()
	currentPid, ok := b.props["pid"].(int)
	b.propsLock.RUnlock()

	if !ok {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{"pid type error"},
		}
	}

	if currentPid < 0 {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{"no active session"},
		}
	}

	err := callClose(currentPid)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	b.propsLock.Lock()
	b.props["pid"] = -1
	b.propsLock.Unlock()

	return fmt.Sprintf("closed: %d", currentPid), nil
}

func (b *BridgeInterface) CloseTerminal() (string, *dbus.Error) {
	b.propsLock.RLock()
	currentPid, ok := b.props["term"].(int)
	b.propsLock.RUnlock()

	if !ok {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{"pid type error"},
		}
	}

	if currentPid < 0 {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{"no active terminal"},
		}
	}

	err := callClose(currentPid)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	b.propsLock.Lock()
	b.props["term"] = -1
	b.propsLock.Unlock()

	return fmt.Sprintf("closed: %d", currentPid), nil
}

func (b *BridgeInterface) Get(iface string, property string) (dbus.Variant, *dbus.Error) {
	b.propsLock.RLock()
	defer b.propsLock.RUnlock()

	if iface != "com.novus.ns.bridge" {
		return dbus.MakeVariant(0), dbus.NewError(
			"org.freedesktop.DBus.Error.UnknownInterface",
			[]interface{}{iface},
		)
	}

	val, ok := b.props[property]
	if !ok {
		return dbus.MakeVariant(0), dbus.NewError(
			"org.freedesktop.DBus.Error.UnknownProperty",
			[]any{property},
		)
	}

	return dbus.MakeVariant(val), nil
}

func (b *BridgeInterface) emitPropertiesChanged(iface string, changed map[string]dbus.Variant, invalidated []string) {
	if b.conn != nil {
		b.conn.Emit("/com/novus/ns", "org.freedesktop.DBus.Properties.PropertiesChanged",
			iface, changed, invalidated)
	}
}

// GetAll implements org.freedesktop.DBus.Properties.GetAll
func (b *BridgeInterface) GetAll(iface string) (map[string]dbus.Variant, *dbus.Error) {
	b.propsLock.RLock()
	defer b.propsLock.RUnlock()

	if iface != "com.novus.ns.bridge" {
		return nil, dbus.NewError(
			"org.freedesktop.DBus.Error.UnknownInterface",
			[]interface{}{iface},
		)
	}

	result := make(map[string]dbus.Variant)
	for k, v := range b.props {
		result[k] = dbus.MakeVariant(v)
	}

	return result, nil
}

// Set implements org.freedesktop.DBus.Properties.Set
func (b *BridgeInterface) Set(iface string, property string, value dbus.Variant) *dbus.Error {
	b.propsLock.Lock()
	defer b.propsLock.Unlock()

	if iface != "com.novus.ns.bridge" {
		return dbus.NewError(
			"org.freedesktop.DBus.Error.UnknownInterface",
			[]interface{}{iface},
		)
	}

	// All properties are read-only in your case
	return dbus.NewError(
		"org.freedesktop.DBus.Error.PropertyReadOnly",
		[]interface{}{property},
	)
}
