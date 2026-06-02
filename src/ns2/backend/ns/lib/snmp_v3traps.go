package lib

import (
	"fmt"
	"slices"
	"strings"
)

type v3Trap struct {
	Version     string `json:"Version"`
	Username    string `json:"Username"`
	EngineId    string `json:"EngineId"`
	Permissions string `json:"Permissions"`
	AuthType    string `json:"AuthType"`
	PrivType    string `json:"PrivType"`
	Protocol    string `json:"Protocol"`
	Host        string `json:"Host"`
	Port        string `json:"Port"`
}

func (trap *v3Trap) ToDict() map[string]string {
	res := map[string]string{}
	res["Version"] = trap.Version
	res["Username"] = trap.Username
	res["EngineId"] = trap.EngineId
	res["Permissions"] = trap.Permissions
	res["AuthType"] = trap.AuthType
	res["PrivType"] = trap.PrivType
	res["Protocol"] = trap.Protocol
	res["Host"] = trap.Host
	res["Port"] = trap.Port
	return res
}

func (trap *v3Trap) FromDict(dict map[string]string) {

	trap.Version = getString(dict, "Version")
	trap.Username = getString(dict, "Username")
	trap.EngineId = getString(dict, "EngineId")
	trap.Permissions = getString(dict, "Permissions")
	trap.AuthType = getString(dict, "AuthType")
	trap.PrivType = getString(dict, "PrivType")
	trap.Protocol = getString(dict, "Protocol")
	trap.Host = getString(dict, "Host")
	trap.Port = getString(dict, "Port")

}

func _readV3TrapsFromFile() ([]v3Trap, error) {

	var traps []v3Trap

	lines, err := GetFileLines(SNMP_CONF_FILE)
	if err != nil {
		return nil, err
	}

	for _, line := range lines {

		if strings.HasPrefix(line, "trapsess -v 3") {
			fields := strings.Fields(line)
			if len(fields) == 14 {
				var trap v3Trap
				trap.Version = fields[2]
				trap.EngineId = fields[4]
				trap.Username = fields[6]
				trap.Permissions = fields[8]
				trap.AuthType = fields[10]
				trap.PrivType = fields[12]

				trap.Protocol = strings.Split(fields[len(fields)-1], ":")[0]
				trap.Host = strings.Split(fields[len(fields)-1], ":")[1]
				trap.Port = strings.Split(fields[len(fields)-1], ":")[2]

				traps = append(traps, trap)
			}

		}
	}

	return traps, nil

}

func _writeV3TrapToFile(trap v3Trap) error {

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

	newTrapLine := fmt.Sprintf("trapsess -v 3 -e %s -u %s -a %s %s:%s:%s", trap.EngineId, trap.Username, trap.AuthType, trap.PrivType, trap.Protocol, trap.Host, trap.Port)
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

func _deleteV3TrapFromConfig(trap v3Trap) error {

	_props := []string{
		trap.Version,
		trap.Username,
		trap.EngineId,
		trap.Permissions,
		trap.AuthType,
		trap.PrivType,
		trap.Protocol,
		trap.Host,
		trap.Port}

	lines, err := GetFileLines(SNMP_CONF_FILE)
	if err != nil {
		return err
	}

	for idx, line := range lines {
		if strings.HasPrefix(line, "trapsess") && HasAll(line, _props) {
			lines = slices.Delete(lines, idx, idx+1)
		}
	}

	err = SetFileLines(SNMP_CONF_FILE, lines)
	if err != nil {
		return err
	}
	return nil
}

func ReadV3Traps() ([]v3Trap, error) {

	traps, err := _readV3TrapsFromFile()
	if err != nil {
		return nil, err
	}

	return traps, nil
}

func AddV3Trap(trap v3Trap) error {

	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	if err := _writeV3TrapToFile(trap); err != nil {
		return err
	}
	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}

	return nil
}

func EditV3Trap(initTrap v3Trap, finalTrap v3Trap) error {

	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	if err := _deleteV3TrapFromConfig(initTrap); err != nil {
		return err
	}

	if err := _writeV3TrapToFile(finalTrap); err != nil {
		return err
	}
	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}

	return nil
}

func DeleteV3Trap(trap v3Trap) error {
	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	if err := _deleteV3TrapFromConfig(trap); err != nil {
		return err
	}
	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}
	return nil
}
