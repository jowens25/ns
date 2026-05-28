package lib

import (
	"fmt"

	"github.com/godbus/dbus/v5"
)

// SnmpInterface implements the com.novus.ns.snmp interface
type SnmpInterface struct{ conn *dbus.Conn }

func (s *SnmpInterface) Test(sender dbus.Sender, message dbus.Message) (string, *dbus.Error) {

	isAuthorized := CheckAuthorization(sender, GetActionId(message))

	if !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{"Not authorized to test snmp"},
		}
	}

	return "HI - AUTH - SUCCESS", nil

}

func (s *SnmpInterface) Reset(sender dbus.Sender, message dbus.Message) (string, *dbus.Error) {

	isAuthorized := CheckAuthorization(sender, GetActionId(message))

	if isAuthorized {

		err := ResetSnmpd()

		if err != nil {
			return "", &dbus.Error{
				Name: "org.freedesktop.DBus.Error",
				Body: []any{err.Error()},
			}
		}

		return "reset complete", nil

	}

	return "", &dbus.Error{
		Name: "org.freedesktop.DBus.Error.AccessDenied",
		Body: []any{"Not authorized to reset snmp"},
	}

}

// CreateV3User creates a V3 user
func (s *SnmpInterface) CreateV3User(sender dbus.Sender, message dbus.Message, v3 map[string]string) (string, *dbus.Error) {

	isAuthorized := CheckAuthorization(sender, GetActionId(message))

	if isAuthorized {
		var newUser v3User
		newUser.FromDict(v3)
		AddV3User(newUser)
		return "added v3 user", nil
	}

	return "", &dbus.Error{
		Name: "org.freedesktop.DBus.Error.AccessDenied",
		Body: []any{"Not authorized to create v3 user"},
	}

}

// GetV3UserByUsername returns a V3 user by username
func (s *SnmpInterface) GetV3UserByUsername(username string) (map[string]string, *dbus.Error) {

	u, err := ReadV3UserByUsername(username)

	if err != nil {
		return nil, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	return u.ToDict(), nil
}

// GetV3Users returns all V3 users
func (s *SnmpInterface) GetV3Users() ([]map[string]string, *dbus.Error) {

	users := []map[string]string{}
	v3s, err := ReadV3Users()

	if err != nil {
		return nil, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	for _, u := range v3s {
		users = append(users, u.ToDict())
	}

	return users, nil

	//return ReadV3Users(), nil
}

// ModifyV3User modifies a V3 user
func (s *SnmpInterface) ModifyV3User(sender dbus.Sender, message dbus.Message, initv3, finv3 map[string]string) (string, *dbus.Error) {

	isAuthorized := CheckAuthorization(sender, GetActionId(message))

	if isAuthorized {
		var initialUser, finalUser v3User
		initialUser.FromDict(initv3)
		finalUser.FromDict(finv3)
		EditV3User(initialUser, finalUser)
		return "user updated", nil
	}

	return "", &dbus.Error{
		Name: "org.freedesktop.DBus.Error.AccessDenied",
		Body: []any{"Not authorized to modify v3 user"},
	}

}

// RemoveV3User removes a V3 user
func (s *SnmpInterface) RemoveV3User(sender dbus.Sender, message dbus.Message, v3Dict map[string]string) (string, *dbus.Error) {

	isAuthorized := CheckAuthorization(sender, GetActionId(message))

	if isAuthorized {
		u := v3User{}
		u.FromDict(v3Dict)
		DeleteV3User(u)
		return "user removed", nil
	}

	return "", &dbus.Error{
		Name: "org.freedesktop.DBus.Error.AccessDenied",
		Body: []any{"Not authorized to remove v3 user"},
	}

}

// CreateV2User creates a V2 user
func (s *SnmpInterface) CreateV2User(sender dbus.Sender, message dbus.Message, v2Dict map[string]string) (string, *dbus.Error) {

	GetUserInfoFromSender(s.conn, sender)

	isAuthorized := CheckAuthorization(sender, GetActionId(message))

	fmt.Println("MESSAGE::::::", message)

	if isAuthorized {
		u := v2User{}

		u.FromDict(v2Dict)
		AddV2User(u)
		return "user created", nil
	}

	return "", &dbus.Error{
		Name: "org.freedesktop.DBus.Error.AccessDenied",
		Body: []any{"Not authorized to create v2 user"},
	}

}

// GetV2UserByCommunity returns a V2 user by community
func (s *SnmpInterface) GetV2UserByCommunity(community string) (map[string]string, *dbus.Error) {

	u, err := ReadV2UserByCommunity(community)

	if err != nil {
		return nil, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	return u.ToDict(), nil
}

// GetV2Users returns all V2 users
func (s *SnmpInterface) GetV2Users() ([]map[string]string, *dbus.Error) {

	users := []map[string]string{}
	v2s, err := ReadV2Users()

	if err != nil {
		return nil, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	for _, u := range v2s {
		users = append(users, u.ToDict())
	}

	return users, nil
}

// ModifyV2User modifies a V2 user
func (s *SnmpInterface) ModifyV2User(sender dbus.Sender, message dbus.Message, v2Dict map[string]string) (string, *dbus.Error) {

	isAuthorized := CheckAuthorization(sender, GetActionId(message))

	if isAuthorized {
		u := v2User{}
		u.FromDict(v2Dict)
		EditV2User(u)

		return "user updated", nil
	}

	return "", &dbus.Error{
		Name: "org.freedesktop.DBus.Error.AccessDenied",
		Body: []any{"Not authorized to modify v2 user"},
	}

}

// RemoveV2User removes a V2 user
func (s *SnmpInterface) RemoveV2User(sender dbus.Sender, message dbus.Message, v2Dict map[string]string) (string, *dbus.Error) {

	isAuthorized := CheckAuthorization(sender, GetActionId(message))

	if isAuthorized {
		u := v2User{}
		u.FromDict(v2Dict)
		DeleteV2User(u)
		return "user removed", nil

	}

	return "", &dbus.Error{
		Name: "org.freedesktop.DBus.Error.AccessDenied",
		Body: []any{"Not authorized to remove v2 user"},
	}

}
