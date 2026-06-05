package lib

import (
	"fmt"
	"log"
	"path/filepath"
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

type snmpGroup struct {
	Permissions  string `json:"Permissions"`
	Version      string `json:"Version"`
	SecurityName string `json:"SecurityName"`
}

// ====================================================================
// SNMP Files and Directories
// ====================================================================

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

	defaultConfigLines, err := GetEmbeddedConfigLines("snmpd.conf")
	if err != nil {
		return err
	}

	err = SetFileLines(SNMP_CONF_FILE, defaultConfigLines)
	if err != nil {
		return err
	}
	return nil
	//return runCmd("cp", "./configs/snmpd.conf", SNMP_CONF_FILE)

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
