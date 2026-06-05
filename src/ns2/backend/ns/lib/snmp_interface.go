package lib

import (
	"log"

	"github.com/godbus/dbus/v5"
)

// SnmpInterface implements the com.novus.ns.snmp interface
type SnmpInterface struct{ conn *dbus.Conn }

// get, create, modify, remove
// ===============================================================================================================================
// v2 users ======================================================================================================================
// ===============================================================================================================================

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

func (s *SnmpInterface) CreateV2User(sender dbus.Sender, message dbus.Message, v2Dict map[string]string) (string, *dbus.Error) {

	GetUserInfoFromSender(s.conn, sender)

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to create v2 user"},
		}
	}

	u := v2User{}

	u.FromDict(v2Dict)
	err := AddV2User(u)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}
	err = s.conn.Emit("/com/novus/ns", "com.novus.ns.snmp.Changed", "V2 user added")
	if err != nil {
		log.Println(err.Error())
	}

	return "user created", nil

}

func (s *SnmpInterface) ModifyV2User(sender dbus.Sender, message dbus.Message, v2Dict map[string]string) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to modify v2 user"},
		}
	}

	u := v2User{}
	u.FromDict(v2Dict)
	err := EditV2User(u)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	err = s.conn.Emit("/com/novus/ns", "com.novus.ns.snmp.Changed", "V2 user updated")
	if err != nil {
		log.Println(err.Error())
	}

	return "user updated", nil

}

func (s *SnmpInterface) RemoveV2User(sender dbus.Sender, message dbus.Message, v2Dict map[string]string) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to remove v2 user"},
		}
	}

	u := v2User{}
	u.FromDict(v2Dict)
	err := DeleteV2User(u)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	err = s.conn.Emit("/com/novus/ns", "com.novus.ns.snmp.Changed", "V2 user removed")
	if err != nil {
		log.Println(err.Error())
	}
	return "user removed", nil

}

// get, create, modify, remove
// ===============================================================================================================================
// v2 traps ======================================================================================================================
// ===============================================================================================================================

func (s *SnmpInterface) GetV2Traps() ([]map[string]string, *dbus.Error) {

	traplist := []map[string]string{}
	traps, err := ReadV2Traps()

	if err != nil {
		return nil, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	for _, u := range traps {
		traplist = append(traplist, u.ToDict())
	}

	return traplist, nil
}

func (s *SnmpInterface) GetV2TrapByCommunity(community string) (map[string]string, *dbus.Error) {

	t, err := ReadV2TrapByCommunity(community)

	if err != nil {
		return nil, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	return t.ToDict(), nil
}

func (s *SnmpInterface) CreateV2Trap(sender dbus.Sender, message dbus.Message, trap map[string]string) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to create v2 trap"},
		}
	}

	var newTrap v2Trap
	newTrap.FromDict(trap)
	err := AddV2Trap(newTrap)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	err = s.conn.Emit("/com/novus/ns", "com.novus.ns.snmp.Changed", "Added v2 Trap")
	if err != nil {
		log.Println(err.Error())
	}

	return "added trap", nil

}

func (s *SnmpInterface) ModifyV2Trap(sender dbus.Sender, message dbus.Message, init, final map[string]string) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to modify v2 trap"},
		}
	}

	var initialTrap, finalTrap v2Trap
	initialTrap.FromDict(init)
	finalTrap.FromDict(final)
	err := EditV2Trap(initialTrap, finalTrap)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	err = s.conn.Emit("/com/novus/ns", "com.novus.ns.snmp.Changed", "Trap updated")
	if err != nil {
		log.Println(err.Error())
	}

	return "trap updated", nil

}

func (s *SnmpInterface) RemoveV2Trap(sender dbus.Sender, message dbus.Message, trap map[string]string) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to remove v2 trap"},
		}
	}

	t := v2Trap{}
	t.FromDict(trap)
	err := DeleteV2Trap(t)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	err = s.conn.Emit("/com/novus/ns", "com.novus.ns.snmp.Changed", "V2 trap removed")
	if err != nil {
		log.Println(err.Error())
	}
	return "trap removed", nil

}

// get, create, modify, remove
// ===============================================================================================================================
// v3 users ======================================================================================================================
// ===============================================================================================================================

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
}

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

func (s *SnmpInterface) CreateV3User(sender dbus.Sender, message dbus.Message, v3 map[string]string) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to create v3 user"},
		}
	}

	var newUser v3User
	newUser.FromDict(v3)
	err := AddV3User(newUser)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	err = s.conn.Emit("/com/novus/ns", "com.novus.ns.snmp.Changed", "Added v3 User")
	if err != nil {
		log.Println(err.Error())
	}

	return "added user", nil

}

func (s *SnmpInterface) ModifyV3User(sender dbus.Sender, message dbus.Message, initv3, finv3 map[string]string) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {

		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to modify v3 user"},
		}

	}

	var initialUser, finalUser v3User
	initialUser.FromDict(initv3)
	finalUser.FromDict(finv3)
	err := EditV3User(initialUser, finalUser)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	err = s.conn.Emit("/com/novus/ns", "com.novus.ns.snmp.Changed", "User updated")
	if err != nil {
		log.Println(err.Error())
	}

	return "user updated", nil

}

// RemoveV3User removes a V3 user
func (s *SnmpInterface) RemoveV3User(sender dbus.Sender, message dbus.Message, v3Dict map[string]string) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {

		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to remove v3 user"},
		}
	}

	u := v3User{}
	u.FromDict(v3Dict)
	err := DeleteV3User(u)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}

	}

	err = s.conn.Emit("/com/novus/ns", "com.novus.ns.snmp.Changed", "User removed")
	if err != nil {
		log.Println(err.Error())
	}

	return "user removed", nil

}

// get, create, modify, delete
// ===============================================================================================================================
// v3 traps ======================================================================================================================
// ===============================================================================================================================

func (s *SnmpInterface) GetV3Traps() ([]map[string]string, *dbus.Error) {

	traplist := []map[string]string{}
	traps, err := ReadV3Traps()

	if err != nil {
		return nil, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	for _, u := range traps {
		traplist = append(traplist, u.ToDict())
	}

	return traplist, nil
}

func (s *SnmpInterface) GetV3TrapByUsername(username string) (map[string]string, *dbus.Error) {

	t, err := ReadV3TrapByUsername(username)

	if err != nil {
		return nil, &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	return t.ToDict(), nil
}

func (s *SnmpInterface) CreateV3Trap(sender dbus.Sender, message dbus.Message, trap map[string]string) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to create v3 trap"},
		}
	}

	var newTrap v3Trap
	newTrap.FromDict(trap)
	err := AddV3Trap(newTrap)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	err = s.conn.Emit("/com/novus/ns", "com.novus.ns.snmp.Changed", "Added v3 Trap")
	if err != nil {
		log.Println(err.Error())
	}

	return "added trap", nil

}

func (s *SnmpInterface) ModifyV3Trap(sender dbus.Sender, message dbus.Message, init, final map[string]string) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to modify v3 trap"},
		}
	}

	var initialTrap, finalTrap v3Trap
	initialTrap.FromDict(init)
	finalTrap.FromDict(final)
	err := EditV3Trap(initialTrap, finalTrap)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	err = s.conn.Emit("/com/novus/ns", "com.novus.ns.snmp.Changed", "Trap updated")
	if err != nil {
		log.Println(err.Error())
	}

	return "trap updated", nil

}

// RemoveV3User removes a V3 user
func (s *SnmpInterface) RemoveV3Trap(sender dbus.Sender, message dbus.Message, trap map[string]string) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to remove v3 user"},
		}
	}

	t := v3Trap{}

	t.FromDict(trap)
	err := DeleteV3Trap(t)
	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}

	}

	err = s.conn.Emit("/com/novus/ns", "com.novus.ns.snmp.Changed", "V3 trap removed")
	if err != nil {
		log.Println(err.Error())
	}

	return "trap removed", nil

}

func (s *SnmpInterface) Reset(sender dbus.Sender, message dbus.Message) (string, *dbus.Error) {

	if isAuthorized := CheckAuthorization(sender, GetActionId(message)); !isAuthorized {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error.AccessDenied",
			Body: []any{"Not authorized to reset snmp"},
		}
	}

	err := ResetSnmpd()

	if err != nil {
		return "", &dbus.Error{
			Name: "org.freedesktop.DBus.Error",
			Body: []any{err.Error()},
		}
	}

	err = s.conn.Emit("/com/novus/ns", "com.novus.ns.snmp.Changed", "Snmp Reset")
	if err != nil {
		log.Println(err.Error())
	}

	return "snmp reset complete", nil

}
