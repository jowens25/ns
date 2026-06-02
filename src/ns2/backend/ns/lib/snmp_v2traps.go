package lib

import (
	"fmt"
	"log"
	"slices"
	"strings"
)

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

func _writeV2TrapToFile(trap v2Trap) error {

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

func ReadV2Traps() ([]v2Trap, error) {
	traps, err := _readV2TrapsFromFile()
	if err != nil {
		return nil, err
	}
	return traps, nil
}
func AddV2Trap(trap v2Trap) error {
	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	if err := _writeV2TrapToFile(trap); err != nil {
		return err
	}
	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}
	return nil
}
func ReadV2TrapByCommunity(community string) (*v2Trap, error) {
	traps, err := ReadV2Traps()
	if err != nil {
		return nil, err
	}

	for _, t := range traps {
		if t.Community == community {
			return &t, nil
		}
	}

	return nil, fmt.Errorf("v2 trap not found")
}

// edits by community name
func EditV2Trap(trap v2Trap) error {

	existingTrap, err := ReadV2TrapByCommunity(trap.Community)
	if err != nil {
		return err
	}

	if existingTrap == nil {
		return fmt.Errorf("no trap found by community")
	}

	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	if err := DeleteV2Trap(*existingTrap); err != nil {
		return err
	}

	if err := _writeV2TrapToFile(trap); err != nil {
		return err
	}
	if err := _startUnit("snmpd.service"); err != nil {
		return err
	}

	return nil
}

func DeleteV2Trap(trap v2Trap) error {

	if err := _stopUnit("snmpd.service"); err != nil {
		return err
	}
	_trap := []string{trap.Version,
		trap.Community,
		trap.Protocol,
		trap.Host,
		trap.Port}

	log.Println("Delete v2 trap")
	lines, err := GetFileLines(SNMP_CONF_FILE)
	if err != nil {
		return err
	}

	for idx, line := range lines {

		if strings.HasPrefix(line, "trapsess") && HasAll(line, _trap) {
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
