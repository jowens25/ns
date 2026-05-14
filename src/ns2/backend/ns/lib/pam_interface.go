package lib

import (
	"fmt"
	"log"

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
		log.Println("pam failed")
		return false, nil
	}
	defer t.CloseSession(pam.Silent)

	if err = t.Authenticate(0); err != nil {
		fmt.Println("invalid cred")
		return false, nil
	}

	fmt.Println("authentication succeeded")

	return true, nil

}
