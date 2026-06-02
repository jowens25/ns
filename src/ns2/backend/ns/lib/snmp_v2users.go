package lib

import (
	"fmt"
	"log"
	"slices"
	"strings"
)

type v2User struct {
	Community    string `json:"Community"`
	Version      string `json:"Version"`
	Permissions  string `json:"Permissions"`
	Source       string `json:"Source"`
	SecurityName string `json:"SecurityName"`
}

func (v2 *v2User) FromDict(dict map[string]string) {

	v2.Community = getString(dict, "Community")
	v2.Version = getString(dict, "Version")
	v2.Permissions = getString(dict, "Permissions")
	v2.Source = getString(dict, "Source")
	v2.SecurityName = getString(dict, "SecurityName")

}

func (v2 *v2User) ToDict() map[string]string {

	res := map[string]string{}
	res["Community"] = v2.Community
	res["Version"] = v2.Version
	res["Permissions"] = v2.Permissions
	res["Source"] = v2.Source
	res["SecurityName"] = v2.SecurityName

	return res

}

func _readV2UsersFromFile() ([]v2User, error) {
	var v2s []v2User
	lines, err := GetFileLines(SNMP_CONF_FILE)
	if err != nil {
		return nil, err
	}
	for _, line := range lines {
		line = strings.TrimSuffix(line, "\n")
		if strings.HasPrefix(line, "com2sec") {
			var v2 v2User
			fields := strings.Fields(line)
			if len(fields) == 4 {
				v2.SecurityName = fields[1]
				v2.Source = fields[2]
				v2.Community = fields[3]
				v2s = append(v2s, v2)
			}
		}
	}

	return v2s, nil
}

func _writeV2UserToFile(user v2User) error {

	users, err := ReadV2Users()
	if err != nil {
		return err
	}

	comNumber := len(users)

	lines, err := GetFileLines(SNMP_CONF_FILE)
	if err != nil {
		return err
	}
	lineCount := 0
	userIndex := -1
	groupIndex := -1

	for _, line := range lines {

		if strings.HasPrefix(line, "#com2sec") {
			userIndex = lineCount + 2 // skip the header and blank line
		}

		if strings.HasPrefix(line, "#group") {
			groupIndex = lineCount + 3
		}

		lineCount++
	}

	newUserLine := fmt.Sprintf("com2sec comuser_%d %s %s", comNumber, user.Source, user.Community)
	newGroupLine := fmt.Sprintf("group %s %s comuser_%d", user.Permissions, user.Version, comNumber)

	if userIndex < 0 {
		lines = append(lines, []string{"#-------------------------------------------------------------------------------"}...)
		lines = append(lines, []string{"#com2sec sec.name source community"}...)
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

	err = SetFileLines(SNMP_CONF_FILE, lines)

	if err != nil {
		return err
	}

	return nil

}

func ReadV2Users() ([]v2User, error) {
	groups, err := _readGroupsFromFile()
	if err != nil {
		return nil, err
	}
	v2s, err := _readV2UsersFromFile()
	if err != nil {
		return nil, err
	}
	for _, g := range groups {
		for i, v2 := range v2s {
			if g.SecurityName == v2.SecurityName {
				v2s[i].SecurityName = g.SecurityName
				v2s[i].Permissions = g.Permissions
				v2s[i].Version = g.Version
			}
		}
	}
	return v2s, nil
}

func AddV2User(user v2User) error {
	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	if err := _writeV2UserToFile(user); err != nil {
		return err
	}
	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}
	return nil
}

func ReadV2UserByCommunity(community string) (*v2User, error) {
	users, err := ReadV2Users()
	if err != nil {
		return nil, err

	}
	for _, u := range users {
		if u.Community == community {
			return &u, nil
		}
	}
	return nil, fmt.Errorf("v2 user not found by community")
}

func ReadV2UserBySecurityName(securityname string) (*v2User, error) {
	users, err := ReadV2Users()
	for _, u := range users {
		if u.SecurityName == securityname {
			return &u, nil
		}
	}
	return nil, err
}

func EditV2User(user v2User) error {

	existingUser, err := ReadV2UserBySecurityName(user.SecurityName)
	if err != nil {
		return err
	}

	if existingUser == nil {
		return fmt.Errorf("no user found by sec name")
	}

	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	if err := DeleteV2User(*existingUser); err != nil {
		return err
	}

	if err := _writeV2UserToFile(user); err != nil {
		return err
	}
	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}

	return nil

}

func DeleteV2User(user v2User) error {

	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	_user := []string{user.SecurityName, user.Source, user.Community}
	_group := []string{user.Permissions, user.Version, user.SecurityName}

	log.Println("Delete v2 user")
	lines, err := GetFileLines(SNMP_CONF_FILE)
	if err != nil {
		return err
	}

	for idx, line := range lines {

		if strings.HasPrefix(line, "com2sec") && HasAll(line, _user) {
			lines = slices.Delete(lines, idx, idx+1)

		}

		if strings.HasPrefix(line, "group") && HasAll(line, _group) {
			lines = slices.Delete(lines, idx, idx+1)

		}
	}

	if err := SetFileLines(SNMP_CONF_FILE, lines); err != nil {
		return err
	}

	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}

	return nil
}
