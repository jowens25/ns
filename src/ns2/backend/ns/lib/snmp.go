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

type snmpGroup struct {
	Permissions  string `json:"Permissions"`
	Version      string `json:"Version"`
	SecurityName string `json:"SecurityName"`
}

type v2Trap struct {
	Version   string `json:"Version"`
	Community string `json:"Community"`
	Protocol  string `json:"Protocol"`
	Host      string `json:"Host"`
	Port      string `json:"Port"`
}

func (trap *v2Trap) ToDict() map[string]string {
	res := map[string]string{}
	res["Version"] = trap.Version
	res["Community"] = trap.Community
	res["Protocol"] = trap.Protocol
	res["Host"] = trap.Host
	res["Port"] = trap.Port
	return res
}

func (trap *v2Trap) FromDict(dict map[string]string) {
	trap.Version = dict["Version"]
	trap.Community = dict["Community"]
	trap.Protocol = dict["Protocol"]
	trap.Host = dict["Host"]
	trap.Port = dict["Port"]

}

// ====================================================================
// SNMP Files and Directories
// ====================================================================

func _readV2TrapsFromFile() ([]v2Trap, error) {

	var traps []v2Trap

	lines, err := GetFileLines(SNMP_CONF_FILE)
	if err != nil {
		return nil, err
	}

	for _, line := range lines {

		if strings.HasPrefix(line, "trapsess -v 1") || strings.HasPrefix(line, "trapsess -v 2c") {
			fields := strings.Fields(line)
			if len(fields) == 6 {
				var trap v2Trap
				trap.Version = fields[2]
				trap.Community = fields[4]
				trap.Protocol = strings.Split(fields[len(fields)-1], ":")[0]
				trap.Host = strings.Split(fields[len(fields)-1], ":")[1]
				trap.Port = strings.Split(fields[len(fields)-1], ":")[2]

				traps = append(traps, trap)
			}
		}
	}

	return traps, nil
}

func _writeV2TrapsToFile(trap v2Trap) error {

	lineCount := 0
	trapIndex := -1

	lines, err := GetFileLines(SNMP_CONF_FILE)
	if err != nil {
		return nil
	}
	for _, line := range lines {

		if strings.HasPrefix(line, "#trapsess") {
			trapIndex = lineCount + 2 // skip the header and blank line
		}

		lineCount++
	}

	newTrapLine := fmt.Sprintf("trapsess -v %s -c %s %s:%s:%s", trap.Version, trap.Community, trap.Protocol, trap.Host, trap.Port)

	if trapIndex < 0 {
		lines = append(lines, []string{"#-------------------------------------------------------------------------------"}...)
		lines = append(lines, []string{"#trapsess [SNMPCMD_ARGS] host"}...)
		lines = append(lines, []string{"#-------------------------------------------------------------------------------"}...)
		lines = append(lines, []string{newTrapLine}...)
	} else {
		lines = append(lines[:trapIndex], append([]string{newTrapLine}, lines[trapIndex:]...)...)
	}

	SetFileLines(SNMP_CONF_FILE, lines)

	return nil

}

func ReadV2Traps() {

}

func _readGroupsFromFile() ([]snmpGroup, error) {

	var groups []snmpGroup
	lines, err := GetFileLines(SNMP_CONF_FILE)
	if err != nil {
		return nil, err
	}
	for _, line := range lines {
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

	return groups, nil
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

func _writeV2User(user v2User) error {

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

func _getPersistentDir() (string, error) {
	lines, err := GetFileLines(SNMP_CONF_FILE)
	if err != nil {
		return "", err
	}
	for _, line := range lines {
		if strings.HasPrefix(line, "persistentDir") {
			fields := strings.Fields(line)
			if len(fields) == 2 {
				return strings.TrimSuffix(fields[1], "\n"), nil
			}
		}
	}
	return "", fmt.Errorf("persistent directory not found in config")
}

func _setPersistentDir(path string) error {
	lines, err := GetFileLines(SNMP_CONF_FILE)
	if err != nil {
		return err
	}
	for i := range lines {
		if strings.HasPrefix(lines[i], "persistentDir") {
			lines[i] = fmt.Sprintf("persistentDir %s", path)
			break

		}
	}
	err = SetFileLines(SNMP_CONF_FILE, lines)

	if err != nil {
		return err
	}
	return nil
}

func _getPersistentConfPath() (string, error) {
	dir, err := _getPersistentDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(dir, "snmpd.conf"), nil
}

func _deletePersistentDir() error {

	dir, err := _getPersistentDir()
	if err != nil {
		return err
	}
	return runCmd("rm", "-rf", dir)
}

func _overwriteWithDefaultSnmpConf() error {
	return runCmd("cp", "./configs/snmpd.conf", SNMP_CONF_FILE)
}

// stops cleans and restarts snmpd
func ResetSnmpd() error {

	// 1. Stop Snmp
	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	// 2. Remove Persistent Dir
	if err := _deletePersistentDir(); err != nil {
		return err
	}
	// 3. Reset Main Config
	if err := _overwriteWithDefaultSnmpConf(); err != nil {
		return err
	}
	// 4. Set Tmp Path for Persistent Dir
	if err := _setPersistentDir("/var/lib/tmp"); err != nil {
		return err
	}
	// 5. Start Snmp
	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}
	// 6. Stop Snmp
	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	// 7. Remove Temp Persistent Dir
	if err := _deletePersistentDir(); err != nil {
		return err
	}
	// 8. Set Real Path for Persistent Dir
	if err := _setPersistentDir("/var/lib/snmp"); err != nil {
		return err
	}
	// 9. Start Snmp
	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}

	log.Println("snmp reset sequence finished")

	return nil
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

func AddV2User(user v2User) error {
	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	if err := _writeV2User(user); err != nil {
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
	return nil, fmt.Errorf("read v2 user by community failed")
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

	existingUser, err := ReadV2UserByCommunity(user.SecurityName)
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

	if err := _writeV2User(user); err != nil {
		return err
	}
	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}

	return nil

}
