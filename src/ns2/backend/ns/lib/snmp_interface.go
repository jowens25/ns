package lib

import (
	"github.com/godbus/dbus/v5"
)

// SnmpInterface implements the com.novus.ns.snmp interface
type SnmpInterface struct{}

func (s *SnmpInterface) TestSnmp(sender dbus.Sender, message dbus.Message) (string, *dbus.Error) {

	isAuthorized, err := CheckAuthorization(sender, GetActionId(message))
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.CheckAuthorizationFailed",
			Body: []any{err.Error()},
		}
	}

	if !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to Test Snmpd"},
		}
	}

	return "HI - AUTH - SUCCESS", nil

}

func (s *SnmpInterface) ResetSnmp(sender dbus.Sender, message dbus.Message) (string, *dbus.Error) {

	isAuthorized, err := CheckAuthorization(sender, GetActionId(message))
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.CheckAuthorizationFailed",
			Body: []any{err.Error()},
		}
	}

	if !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to reset snmp"},
		}
	}

	return ResetSnmpd(), nil

}

// CreateV3User creates a V3 user
func (s *SnmpInterface) CreateV3User(v3 map[string]string) (string, *dbus.Error) {
	var newUser v3User
	newUser.FromDict(v3)
	AddV3User(newUser)
	return "added v3User", nil
}

// GetV3UserByUsername returns a V3 user by username
func (s *SnmpInterface) GetV3UserByUsername(username string) (*v3User, *dbus.Error) {
	return ReadV3UserByUsername(username), nil
}

// GetV3Users returns all V3 users
func (s *SnmpInterface) GetV3Users() ([]v3User, *dbus.Error) {
	return ReadV3Users(), nil
}

// ModifyV3User modifies a V3 user
func (s *SnmpInterface) ModifyV3User(initv3, finv3 map[string]string) *dbus.Error {
	var initialUser, finalUser v3User
	initialUser.FromDict(initv3)
	finalUser.FromDict(finv3)
	EditV3User(initialUser, finalUser)
	return nil
}

// RemoveV3User removes a V3 user
func (s *SnmpInterface) RemoveV3User(v3Dict map[string]string) *dbus.Error {
	u := v3User{}
	u.FromDict(v3Dict)
	DeleteV3User(u)
	return nil
}

// CreateV2User creates a V2 user
func (s *SnmpInterface) CreateV2User(v2Dict map[string]string) *dbus.Error {
	u := v2User{}
	u.FromDict(v2Dict)
	AddV2User(u)
	return nil
}

// GetV2UserByCommunity returns a V2 user by community
func (s *SnmpInterface) GetV2UserByCommunity(community string) (v2User, *dbus.Error) {

	return *ReadV2UserByCommunity(community), nil
}

// GetV2Users returns all V2 users
func (s *SnmpInterface) GetV2Users() ([]v2User, *dbus.Error) {
	return ReadV2Users(), nil
}

// ModifyV2User modifies a V2 user
func (s *SnmpInterface) ModifyV2User(v2Dict map[string]string) *dbus.Error {

	u := v2User{}
	u.FromDict(v2Dict)
	EditV2User(u)

	return nil
}

// RemoveV2User removes a V2 user
func (s *SnmpInterface) RemoveV2User(v2Dict map[string]string) *dbus.Error {

	//CheckPolkit()

	u := v2User{}
	u.FromDict(v2Dict)
	DeleteV2User(u)
	return nil
}
