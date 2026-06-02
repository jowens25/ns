package lib

import (
	"fmt"
	"log"
	"slices"
	"strings"
)

type v3User struct {
	Username       string `json:"Username"`
	Version        string `json:"Version"`
	EngineId       string `json:"EngineId"`
	AuthType       string `json:"AuthType"`
	AuthPassphrase string `json:"AuthPassphrase"`
	PrivType       string `json:"PrivType"`
	PrivPassphrase string `json:"PrivPassphrase"`
	Permissions    string `json:"Permissions"`
}

func (v3 *v3User) FromDict(dict map[string]string) {
	v3.Username = dict["Username"]
	v3.Version = dict["Version"]
	v3.AuthType = dict["AuthType"]
	v3.AuthPassphrase = dict["AuthPassphrase"]
	v3.PrivType = dict["PrivType"]
	v3.PrivPassphrase = dict["PrivPassphrase"]
	v3.Permissions = dict["Permissions"]
}

func (v3 *v3User) ToDict() map[string]string {

	res := map[string]string{}

	res["Username"] = v3.Username
	res["Version"] = v3.Version
	res["EngineId"] = v3.EngineId
	res["AuthType"] = v3.AuthType
	res["AuthPassphrase"] = v3.AuthPassphrase
	res["PrivType"] = v3.PrivType
	res["PrivPassphrase"] = v3.PrivPassphrase
	res["Permissions"] = v3.Permissions

	return res

}

func _readV3UsersFromFile() ([]v3User, error) {

	var v3s []v3User
	log.Println("_readv3Usersfromfile...")
	dir, err := _getPersistentConfPath()
	if err != nil {
		return nil, err
	}
	lines, err := GetFileLines(dir)
	if err != nil {
		return nil, err
	}
	for _, line := range lines {

		line = strings.TrimSuffix(line, "\n")

		if strings.HasPrefix(line, "usmUser") {

			var v3 v3User

			fields := strings.Fields(line)
			if len(fields) == 12 {
				v3.Username = strings.Trim(fields[4], `"`)
				v3.EngineId = fields[3]
				v3.AuthType = USM_OID_MAP[fields[7]]
				v3.PrivType = USM_OID_MAP[fields[9]]

				v3s = append(v3s, v3)

			}

		}

	}

	return v3s, nil
}

func _writeV3UserCreateDirective(user v3User) error {

	lineCount := 0
	userIndex := -1
	groupIndex := -1

	lines, err := GetFileLines(SNMP_CONF_FILE)
	if err != nil {
		return nil
	}
	for _, line := range lines {

		if strings.HasPrefix(line, "#com2sec") {
			userIndex = lineCount + 2 // skip the header and blank line
		}

		if strings.HasPrefix(line, "#group") {
			groupIndex = lineCount + 3
		}

		lineCount++
	}

	newUserLine := fmt.Sprintf("createUser %s %s %s %s %s", user.Username, user.AuthType, user.AuthPassphrase, user.PrivType, user.PrivPassphrase)
	newGroupLine := fmt.Sprintf("group %s %s %s", user.Permissions, user.Version, user.Username)

	if userIndex < 0 {
		lines = append(lines, []string{"#-------------------------------------------------------------------------------"}...)
		lines = append(lines, []string{"#createUser username [MD5|SHA] [passphrase] [DES] [passphrase]"}...)
		lines = append(lines, []string{"#-------------------------------------------------------------------------------"}...)
		lines = append(lines, []string{newUserLine}...)
	} else {
		lines = append(lines[:userIndex], append([]string{newUserLine}, lines[userIndex:]...)...)
	}

	if groupIndex < 0 {
		lines = append(lines, []string{"#-------------------------------------------------------------------------------"}...)
		lines = append(lines, []string{"#group  group name      sec.model  sec.name"}...)
		lines = append(lines, []string{"#-------------------------------------------------------------------------------"}...)
		lines = append(lines, []string{newGroupLine}...)

	} else {
		lines = append(lines[:groupIndex], append([]string{newGroupLine}, lines[groupIndex:]...)...)
	}

	SetFileLines(SNMP_CONF_FILE, lines)

	return nil

}

func _deleteV3UserFromStorage(user v3User) error {

	dir, err := _getPersistentConfPath()
	if err != nil {
		return err
	}

	lines, err := GetFileLines(dir)
	if err != nil {
		return err
	}
	for idx, line := range lines {

		if strings.HasPrefix(line, "usmUser") {
			fields := strings.Fields(line)
			temp_auth_type, ok := USM_OID_MAP[fields[7]]

			if !ok {
				log.Println("Error v3 del with USM OID MAP 7")
			}

			temp_priv_type, ok := USM_OID_MAP[fields[9]]
			if !ok {
				log.Println("Error v3 del with USM OID MAP 9")

			}

			if strings.Contains(line, user.Username) && temp_auth_type == user.AuthType && temp_priv_type == user.PrivType {
				lines = slices.Delete(lines, idx, idx+1)

			}
		}
	}

	err = SetFileLines(dir, lines)
	if err != nil {
		return err
	}
	return nil
}

func _deleteV3UserCreateDirective(user v3User) error {

	_props := []string{
		user.Username,
		user.AuthType,
		user.AuthPassphrase,
		user.PrivType,
		user.AuthPassphrase}

	lines, err := GetFileLines(SNMP_CONF_FILE)

	if err != nil {
		return err
	}

	for idx, line := range lines {

		if strings.HasPrefix(line, "createUser") && HasAll(line, _props) {
			lines = slices.Delete(lines, idx, idx+1)
		}
	}

	err = SetFileLines(SNMP_CONF_FILE, lines)
	if err != nil {
		return err
	}
	return nil
}

func _deleteV3UserFromConfig(user v3User) error {

	_props := []string{
		user.Permissions,
		user.Version,
		user.Username,
	}

	lines, err := GetFileLines(SNMP_CONF_FILE)

	if err != nil {
		return err
	}

	for idx, line := range lines {
		if strings.HasPrefix(line, "group") && HasAll(line, _props) {
			lines = slices.Delete(lines, idx, idx+1)
		}
	}

	err = SetFileLines(SNMP_CONF_FILE, lines)

	if err != nil {
		return err
	}
	return nil
}

func ReadV3UserByUsername(username string) (*v3User, error) {
	users, err := ReadV3Users()
	if err != nil {
		return nil, err
	}
	for _, u := range users {
		if u.Username == username {
			return &u, nil
		}
	}
	return nil, fmt.Errorf("v3 user not found by username")
}

func ReadV3Users() ([]v3User, error) {

	groups, err := _readGroupsFromFile()
	if err != nil {
		return nil, err
	}
	v3s, err := _readV3UsersFromFile()
	if err != nil {
		return nil, err
	}

	for _, g := range groups {

		for i, v3 := range v3s {

			if g.SecurityName == v3.Username {
				v3s[i].Permissions = g.Permissions
				v3s[i].Version = g.Version

			}
		}
	}

	return v3s, nil
}

func AddV3User(user v3User) error {

	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	if err := _writeV3UserCreateDirective(user); err != nil {
		return err
	}
	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}
	if err := _deleteV3UserCreateDirective(user); err != nil {
		return err
	}
	return nil
}

func EditV3User(initUser v3User, finalUser v3User) error {

	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	if err := _deleteV3UserFromStorage(initUser); err != nil {
		return err
	}
	if err := _deleteV3UserFromConfig(initUser); err != nil {
		return err
	}
	if err := _writeV3UserCreateDirective(finalUser); err != nil {
		return err
	}
	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}
	if err := _deleteV3UserCreateDirective(finalUser); err != nil {
		return err
	}
	return nil
}

func DeleteV3User(user v3User) error {
	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	if err := _deleteV3UserFromConfig(user); err != nil {
		return err
	}
	if err := _deleteV3UserFromStorage(user); err != nil {
		return err
	}
	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}
	return nil
}
