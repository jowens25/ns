package lib

import (
	"fmt"
	"log"
	"path/filepath"
	"slices"
	"strings"
)

var SNMP_CONF_FILE string = "/etc/snmp/snmpd.conf.d/novus-snmpd.conf"
var DEFAULT_PERSISTENT_DIR_PATH string = "/var/lib/snmp"

var USM_OID_MAP = map[string]string{
	// Authentication Protocols (RFC 3414)
	"1.3.6.1.6.3.10.1.1.1":  "NoAuth",
	".1.3.6.1.6.3.10.1.1.2": "MD5",
	".1.3.6.1.6.3.10.1.1.3": "SHA",
	"1.3.6.1.6.3.10.1.1.4":  "HMAC-SHA2-224",
	"1.3.6.1.6.3.10.1.1.5":  "HMAC-SHA2-256",
	// Privacy Protocols (RFC 3414 + 3826)
	"1.3.6.1.6.3.10.1.2.1":  "NoPriv",
	".1.3.6.1.6.3.10.1.2.2": "DES",
	".1.3.6.1.6.3.10.1.2.4": "AES",
	"1.3.6.1.6.3.10.1.2.5":  "AES-192",
	"1.3.6.1.6.3.10.1.2.6":  "AES-256",
}

type v2User struct {
	Community    string `json:"Community"`
	Version      string `json:"Version"`
	Permissions  string `json:"Permissions"`
	Source       string `json:"Source"`
	SecurityName string `json:"SecurityName"`
}

func getString(dict map[string]string, key string) string {

	v, ok := dict[key]

	if !ok {
		return ""
	}

	return v

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

type v3User struct {
	Username       string `json:"Username"`
	Version        string `json:"Version"`
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
	res["AuthType"] = v3.AuthType
	res["AuthPassphrase"] = v3.AuthPassphrase
	res["PrivType"] = v3.PrivType
	res["PrivPassphrase"] = v3.PrivPassphrase
	res["Permissions"] = v3.Permissions

	return res

}

type snmpGroup struct {
	Permissions  string `json:"Permissions"`
	Version      string `json:"Version"`
	SecurityName string `json:"SecurityName"`
}

type snmpTrap struct {
}

// ====================================================================
// SNMP Files and Directories
// ====================================================================

func _readGroupsFromFile() []snmpGroup {

	var groups []snmpGroup
	for _, line := range GetFileLines(SNMP_CONF_FILE) {
		if strings.HasPrefix(line, "group") {
			fields := strings.Fields(line)
			var g snmpGroup
			if len(fields) == 4 {
				g.Permissions = fields[1]
				g.Version = fields[2]
				g.SecurityName = fields[3]
				groups = append(groups, g)
			}
		}
	}

	return groups
}

func _readV2UsersFromFile() []v2User {
	var v2s []v2User
	for _, line := range GetFileLines(SNMP_CONF_FILE) {
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

	return v2s
}

func _readV3UsersFromFile() []v3User {

	var v3s []v3User
	log.Println("_readv3Usersfromfile...")
	for _, line := range GetFileLines(_getPersistentConfPath()) {

		line = strings.TrimSuffix(line, "\n")

		if strings.HasPrefix(line, "usmUser") {

			var v3 v3User

			fields := strings.Fields(line)
			if len(fields) == 12 {
				v3.Username = strings.Trim(fields[4], `"`)

				v3.AuthType = USM_OID_MAP[fields[7]]
				v3.PrivType = USM_OID_MAP[fields[9]]

				v3s = append(v3s, v3)

			}

		}

	}

	return v3s
}

func ReadV2Users() []v2User {
	groups := _readGroupsFromFile()
	v2s := _readV2UsersFromFile()
	for _, g := range groups {
		for i, v2 := range v2s {
			if g.SecurityName == v2.SecurityName {
				v2s[i].SecurityName = g.SecurityName
				v2s[i].Permissions = g.Permissions
				v2s[i].Version = g.Version
			}
		}
	}
	return v2s
}

func _writeV2User(user v2User) {

	comNumber := len(ReadV2Users())

	lines := GetFileLines(SNMP_CONF_FILE)

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

	SetFileLines(SNMP_CONF_FILE, lines)

}

func _writeV3UserCreateDirective(user v3User) {

	lineCount := 0
	userIndex := -1
	groupIndex := -1

	lines := GetFileLines(SNMP_CONF_FILE)

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

}

func _deleteV3UserFromStorage(user v3User) {

	lines := GetFileLines(_getPersistentConfPath())
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

	SetFileLines(_getPersistentConfPath(), lines)
}

func _deleteV3UserCreateDirective(user v3User) {

	_props := []string{
		user.Username,
		user.AuthType,
		user.AuthPassphrase,
		user.PrivType,
		user.AuthPassphrase}

	lines := GetFileLines(SNMP_CONF_FILE)

	for idx, line := range lines {

		if strings.HasPrefix(line, "createUser") && HasAll(line, _props) {
			lines = slices.Delete(lines, idx, idx+1)
		}
	}

	SetFileLines(SNMP_CONF_FILE, lines)

}

func _deleteV3UserFromConfig(user v3User) {

	_props := []string{
		user.Permissions,
		user.Version,
		user.Username,
	}

	lines := GetFileLines(SNMP_CONF_FILE)

	for idx, line := range lines {
		if strings.HasPrefix(line, "group") && HasAll(line, _props) {
			lines = slices.Delete(lines, idx, idx+1)
		}
	}

	SetFileLines(SNMP_CONF_FILE, lines)

}

func _getPersistentDir() string {

	for _, line := range GetFileLines(SNMP_CONF_FILE) {
		if strings.HasPrefix(line, "persistentDir") {
			fields := strings.Fields(line)
			if len(fields) == 2 {
				return strings.TrimSuffix(fields[1], "\n")
			}
		}
	}
	return "notfound"
}

func _setPersistentDir(path string) {
	lines := GetFileLines(SNMP_CONF_FILE)
	for i := range lines {
		if strings.HasPrefix(lines[i], "persistentDir") {
			lines[i] = fmt.Sprintf("persistentDir %s", path)
			break

		}
	}
	SetFileLines(SNMP_CONF_FILE, lines)

}

func _getPersistentConfPath() string {
	return filepath.Join(_getPersistentDir(), "snmpd.conf")
}

func _deletePersistentDir() error {
	return runCmd("rm", "-rf", _getPersistentDir())
}

func _overwriteWithDefaultSnmpConf() error {
	return runCmd("cp", "./configs/snmpd.conf", SNMP_CONF_FILE)
}

// stops cleans and restarts snmpd
func ResetSnmpd() error {

	// 1. Stop Snmp
	err := _stopUnit("snmpd.service")
	if err != nil {
		return err
	}
	// 2. Remove Persistent Dir
	err = _deletePersistentDir()
	if err != nil {
		return err
	}
	// 3. Reset Main Config
	err = _overwriteWithDefaultSnmpConf()
	if err != nil {
		return err
	}
	// 4. Set Tmp Path for Persistent Dir
	_setPersistentDir("/var/lib/tmp")
	// 5. Start Snmp
	_startUnit("snmpd.service")
	// 6. Stop Snmp
	_stopUnit("snmpd.service")
	// 7. Remove Temp Persistent Dir
	_deletePersistentDir()
	// 8. Set Real Path for Persistent Dir
	_setPersistentDir("/var/lib/snmp")
	// 9. Start Snmp
	_startUnit("snmpd.service")

	log.Println("snmp reset sequence finished")

	return nil
}

func AddV3User(user v3User) {

	_stopUnit("snmpd.service")
	_writeV3UserCreateDirective(user)
	_startUnit("snmpd.service")
	_deleteV3UserCreateDirective(user)
}

func ReadV3UserByUsername(username string) *v3User {

	for _, u := range ReadV3Users() {
		if u.Username == username {
			return &u
		}
	}
	return nil
}

func ReadV3Users() []v3User {

	groups := _readGroupsFromFile()
	v3s := _readV3UsersFromFile()

	for _, g := range groups {

		for i, v3 := range v3s {

			if g.SecurityName == v3.Username {
				v3s[i].Permissions = g.Permissions
				v3s[i].Version = g.Version

			}
		}
	}

	return v3s
}

func EditV3User(initUser v3User, finalUser v3User) {

	_stopUnit("snmpd.service")
	_deleteV3UserFromStorage(initUser)
	_deleteV3UserFromConfig(initUser)
	_writeV3UserCreateDirective(finalUser)
	_startUnit("snmpd.service")
	_deleteV3UserCreateDirective(finalUser)
}

func DeleteV3User(user v3User) {
	_stopUnit("snmpd.service")
	_deleteV3UserFromConfig(user)
	_deleteV3UserFromStorage(user)
	_startUnit("snmpd.service")
}

func AddV2User(user v2User) {
	_stopUnit("snmpd.service")
	_writeV2User(user)
	_startUnit("snmpd.service")
}

func DeleteV2User(user v2User) {

	_stopUnit("snmpd.service")
	_user := []string{user.SecurityName, user.Source, user.Community}
	_group := []string{user.Permissions, user.Version, user.SecurityName}

	log.Println("Delete v2 user")
	lines := GetFileLines(SNMP_CONF_FILE)

	for idx, line := range lines {

		if strings.HasPrefix(line, "com2sec") && HasAll(line, _user) {
			lines = slices.Delete(lines, idx, idx+1)

		}

		if strings.HasPrefix(line, "group") && HasAll(line, _group) {
			lines = slices.Delete(lines, idx, idx+1)

		}
	}

	SetFileLines(SNMP_CONF_FILE, lines)

	_startUnit("snmpd.service")

}

func ReadV2UserByCommunity(community string) *v2User {
	for _, u := range ReadV2Users() {
		if u.Community == community {
			return &u
		}
	}
	return nil
}

func ReadV2UserBySecurityName(securityname string) *v2User {
	for _, u := range ReadV2Users() {
		if u.SecurityName == securityname {
			return &u
		}
	}
	return nil
}

func EditV2User(user v2User) {

	existingUser := ReadV2UserByCommunity(user.SecurityName)

	if existingUser == nil {
		log.Fatal("no user found by sec name")
	}

	_stopUnit("snmpd.service")
	DeleteV2User(*existingUser)
	_writeV2User(user)
	_startUnit("snmpd.service")

}
