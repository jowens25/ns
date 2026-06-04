package lib

import (
	"github.com/godbus/dbus/v5"
	"github.com/msteinert/pam"
)

// PamInterface implements the com.novus.ns.pam interface
type PamInterface struct{}

func (p *PamInterface) Authenticate(user string, password string) (bool, *dbus.Error) {

	// Start PAM transaction
	t, err := pam.StartFunc("login", user, func(s pam.Style, msg string) (string, error) {
		switch s {
		case pam.PromptEchoOff:
			return password, nil
		case pam.PromptEchoOn:
			return user, nil
		}
		return "", nil
	})

	if err != nil {
		return false, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	defer t.CloseSession(pam.Silent)

	err = t.Authenticate(0)
	if err != nil {
		return false, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}

	}

	return true, nil

}
