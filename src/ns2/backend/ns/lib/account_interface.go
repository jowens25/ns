package lib

import (
	"fmt"
	"log"

	"github.com/godbus/dbus/v5"
)

// AccountsInterface implements the com.novus.ns.accounts interface
type AccountInterface struct {
	conn *dbus.Conn
}

// get all users
// make admins
// make users
// delete users
// change password

func (a *AccountInterface) SetPasswordPolicy(policy map[string]any, sender dbus.Sender, message dbus.Message) *dbus.Error {

	isAuthorized := CheckAuthorization(sender, GetActionId(message))

	if isAuthorized {
		err := SetPolicy(policy)
		if err != nil {
			return &dbus.Error{
				Name: "org.freedesktop.DBus.Error",
				Body: []any{err.Error()},
			}

		}
		err = a.conn.Emit("/com/novus/ns", "com.novus.ns.accounts.Changed", "SetPasswordPolicy")
		if err != nil {
			log.Println(err.Error())
		}
		return nil
	}

	return &dbus.Error{
		Name: "org.freedesktop.DBus.Error.AccessDenied",
		Body: []any{"Not authorized to set password policy"},
	}

}

func (a *AccountInterface) GetPasswordPolicy() (map[string]any, *dbus.Error) {

	policy, err := GetPolicy()
	if err != nil {
		return nil, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}

	}

	return map[string]any{
		"max":    policy.MaxLength,
		"min":    policy.MinLength,
		"upper":  policy.RequireUppercase,
		"lower":  policy.RequireLowercase,
		"digit":  policy.RequireDigit,
		"symbol": policy.RequireSymbol,
	}, nil

}

func (a *AccountInterface) ValidatePassword(password string) (bool, *dbus.Error) {

	isValid, err := Validate(password)
	if err != nil {
		return false, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}

	}

	return isValid, nil

}

func (a *AccountInterface) AddUser(username string, password string, sender dbus.Sender, message dbus.Message) (string, *dbus.Error) {

	isAuthorized := CheckAuthorization(sender, GetActionId(message))

	if isAuthorized {
		err := MakeNewUser(username, password)
		if err != nil {
			return "", &dbus.Error{
				Name: "org.freedesktop.DBus.Error",
				Body: []any{err.Error()},
			}

		}

		err = a.conn.Emit("/com/novus/ns", "com.novus.ns.accounts.Changed", "AddUser")
		if err != nil {
			log.Println(err.Error())
		}

		return fmt.Sprintf("added %s", username), nil

	}

	return "", &dbus.Error{
		Name: "org.freedesktop.DBus.Error.AccessDenied",
		Body: []any{"Not authorized to add user"},
	}

}

func (a *AccountInterface) AddAdmin(username string, password string, sender dbus.Sender, message dbus.Message) (string, *dbus.Error) {

	isAuthorized := CheckAuthorization(sender, GetActionId(message))

	if isAuthorized {
		err := MakeNewAdmin(username, password)
		if err != nil {
			return "", &dbus.Error{
				Name: "org.freedesktop.DBus.Error",
				Body: []any{err.Error()},
			}

		}
		err = a.conn.Emit("/com/novus/ns", "com.novus.ns.accounts.Changed", "AddAdmin")
		if err != nil {
			log.Println(err.Error())
		}

		return fmt.Sprintf("added %s", username), nil

	}

	return "", &dbus.Error{
		Name: "org.freedesktop.DBus.Error.AccessDenied",
		Body: []any{"Not authorized to add admin"},
	}

}

func (a *AccountInterface) Remove(sender dbus.Sender, message dbus.Message, username string) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); isAuthorized {

		numAdmins, err := GetNumberOfAdmins()
		if err != nil {
			return "", &dbus.Error{
				Name: "org.freedesktop.DBus.Error",
				Body: []any{err.Error()},
			}

		}
		if numAdmins > 1 {
			err = RemoveUser(username)
			if err != nil {
				return "", &dbus.Error{
					Name: "org.freedesktop.DBus.Error",
					Body: []any{err.Error()},
				}

			}
			err = a.conn.Emit("/com/novus/ns", "com.novus.ns.accounts.Changed", "Remove")
			if err != nil {
				log.Println(err.Error())
			}
			return fmt.Sprintf("removed %s", username), nil

		} else {
			return "", &dbus.Error{
				Name: "org.freedesktop.DBus.Error",
				Body: []any{"cannot remove the last admin"},
			}

		}

	}

	return "", &dbus.Error{
		Name: "org.freedesktop.DBus.Error.AccessDenied",
		Body: []any{"Not authorized to remove users"},
	}
}

func (a *AccountInterface) GetUsers() ([]map[string]string, *dbus.Error) {

	log.Println("get Users")

	users, err := getUserAndAdmins()

	if err != nil {

		return nil, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	return users, nil

}

func (a *AccountInterface) UpdatePassword(username string, newpassword string, sender dbus.Sender, message dbus.Message) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); isAuthorized {

		err := ChangePassword(username, newpassword)
		if err != nil {
			return "", &dbus.Error{
				Name: "org.freedesktop.DBus.Error",
				Body: []any{err.Error()},
			}

		}
		err = a.conn.Emit("/com/novus/ns", "com.novus.ns.accounts.Changed", "UpdatePassword")
		if err != nil {
			log.Println(err.Error())
		}
		return "password updated", nil

	}

	return "", &dbus.Error{
		Name: "org.freedesktop.DBus.Error.AccessDenied",
		Body: []any{"Not authorized to remove users"},
	}
}
