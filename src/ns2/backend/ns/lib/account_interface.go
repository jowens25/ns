package lib

import (
	"github.com/godbus/dbus/v5"
)

// AccountsInterface implements the com.novus.ns.accounts interface
type AccountInterface struct{}

func (a *AccountInterface) AddUser() *dbus.Error    { return nil }
func (a *AccountInterface) RemoveUser() *dbus.Error { return nil }
func (a *AccountInterface) AddSystemUser(username string, sender dbus.Sender) (string, *dbus.Error) {

	return "User created: " + username, nil
}
