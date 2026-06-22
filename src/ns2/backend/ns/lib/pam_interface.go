package lib

import (
	"context"
	"sync"

	"github.com/godbus/dbus/v5"
	"github.com/msteinert/pam"
)

// PamInterface implements the com.novus.ns.pam interface
type PamInterface struct{}

type activeSession struct {
	t      *pam.Transaction
	cancel context.CancelFunc
}

var sessions sync.Map // map[string]*activeSession

func (p *PamInterface) Authenticate(username string, password string) (bool, *dbus.Error) {

	t, err := pam.StartFunc("login", username, func(s pam.Style, msg string) (string, error) {
		switch s {
		case pam.PromptEchoOff:
			return password, nil
		case pam.PromptEchoOn:
			return username, nil
		}
		return "", nil
	})

	if err != nil {
		return false, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	if err = t.Authenticate(0); err != nil {
		return false, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	return true, nil

}

func (p *PamInterface) ResetDefaultConfig(sender dbus.Sender, message dbus.Message) *dbus.Error {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {
		return &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to factory reset"},
		}
	}

	err := FactoryReset()

	if err != nil {
		return &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	return nil

}
