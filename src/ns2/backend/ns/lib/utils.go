package lib

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"

	"github.com/godbus/dbus/v5"
)

// returns slice of file content split with \n
func GetFileLines(path string) ([]string, error) {

	content, err := os.ReadFile(path)
	if err != nil {
		log.Println("get file lines: failed to read: ", path)
		log.Println(err.Error())

		return []string{}, err
	}

	return strings.Split(string(content), "\n"), nil
}

func SetFileLines(path string, lines []string) error {
	err := os.WriteFile(path, []byte(strings.Join(lines, "\n")), 0644)
	if err != nil {
		return err
	}
	return nil
}

func runCmd(cmd string, args ...string) error {

	out, err := exec.Command(cmd, args...).CombinedOutput()

	if err != nil {

		return fmt.Errorf("runCmd failed callling: %s with: %s -> out: %s", cmd, err.Error(), string(out))
	}

	return nil

}

func runCmdWithStdin(stdin string, cmd string, args ...string) error {
	c := exec.Command(cmd, args...)
	c.Stdin = strings.NewReader(stdin) // e.g. "username:newpassword\n"

	out, err := c.CombinedOutput()
	if err != nil {
		return fmt.Errorf("runCmdWithStdin failed: %s -> out: %s", err, string(out))
	}
	return nil
}

func HasAll(line string, elements []string) bool {

	for _, e := range elements {

		if !strings.Contains(line, e) {
			return false
		}

	}
	return true
}

func getString(dict map[string]string, key string) string {

	v, ok := dict[key]

	if !ok {
		return ""
	}

	return v

}

func FactoryReset() error {
	var interfaceString string = "eth"
	rsp, err := Call(
		"org.freedesktop.NetworkManager",
		"/org/freedesktop/NetworkManager",
		"org.freedesktop.NetworkManager.GetDevices",
		[]any{})

	if err != nil {
		return err
	}

	devicePaths := rsp

	for _, p := range devicePaths.([]dbus.ObjectPath) {

		rsp, err := Call(
			"org.freedesktop.NetworkManager",
			p,
			"org.freedesktop.DBus.Properties.Get",
			[]any{"org.freedesktop.NetworkManager.Device", "DeviceType"})

		if err != nil {
			return err
		}

		deviceType := rsp.(uint32)

		if deviceType == 1 {
			rsp, err := CallReturnBody(
				"org.freedesktop.NetworkManager",
				p,
				"org.freedesktop.DBus.Properties.Get",
				[]any{"org.freedesktop.NetworkManager.Device", "Interface"})

			if err != nil {
				return err
			}

			interfaceName := rsp.([]any)[0]

			interfaceString = interfaceName.(dbus.Variant).Value().(string)

			log.Printf("Network: wired interface found %s\n", interfaceString)

			settings := map[string]map[string]dbus.Variant{
				"connection": {
					"id": dbus.MakeVariant(interfaceString),
				},
				"ipv4": {
					"method": dbus.MakeVariant("manual"),
					"address-data": dbus.MakeVariant([]map[string]dbus.Variant{
						{
							"address": dbus.MakeVariant("192.168.7.224"),
							"prefix":  dbus.MakeVariant(uint32(24)),
						},
					}),
					"gateway": dbus.MakeVariant("192.168.7.254"),
					"dns-data": dbus.MakeVariant([]string{
						"8.8.8.8",
						"8.8.4.4",
					}),
				},
			}

			rsp, err = CallReturnBody(
				"org.freedesktop.NetworkManager",
				"/org/freedesktop/NetworkManager",
				"org.freedesktop.NetworkManager.AddAndActivateConnection", []any{settings, p, dbus.ObjectPath("/")})

			if err != nil {
				return err
			}

			log.Println("Network: set up new connection for wired interface")

			//fmt.Println(rsp)
			break

		}

	}

	rsp, err = Call(
		"org.fedoraproject.FirewallD1",
		"/org/fedoraproject/FirewallD1",
		"org.fedoraproject.FirewallD1.setDefaultZone",
		[]any{"public"})

	if err != nil {
		log.Println(err.Error())
	} else {
		log.Println(rsp)
	}

	log.Println("Firewall: Default zone set to public")

	rsp, err = Call(
		"org.fedoraproject.FirewallD1",
		"/org/fedoraproject/FirewallD1",
		"org.fedoraproject.FirewallD1.zone.changeZoneOfInterface",
		[]any{"", interfaceString})

	if err != nil {
		return err
	}
	//log.Println(rsp)
	log.Printf("Firewall: Set %s to default zone\n", interfaceString)

	rsp, err = Call("org.fedoraproject.FirewallD1",
		"/org/fedoraproject/FirewallD1",
		"org.fedoraproject.FirewallD1.zone.addService",
		[]any{"public", "https", 0})

	if err != nil {
		log.Println(err.Error())
	} else {
		log.Println("Firewall: added https")
	}

	rsp, err = Call("org.fedoraproject.FirewallD1",
		"/org/fedoraproject/FirewallD1",
		"org.fedoraproject.FirewallD1.zone.addService",
		[]any{"public", "ssh", 0})

	if err != nil {
		log.Println(err.Error())
	} else {
		log.Println("Firewall: added ssh")
	}

	rsp, err = Call("org.fedoraproject.FirewallD1",
		"/org/fedoraproject/FirewallD1",
		"org.fedoraproject.FirewallD1.zone.addService",
		[]any{"public", "snmp", 0})

	if err != nil {
		log.Println(err.Error())
	} else {
		log.Println("Firewall: added snmp")
	}

	rsp, err = Call("org.fedoraproject.FirewallD1",
		"/org/fedoraproject/FirewallD1",
		"org.fedoraproject.FirewallD1.zone.addService",
		[]any{"public", "snmptrap", 0})

	if err != nil {
		log.Println(err.Error())
	} else {
		log.Println("Firewall: added snmptrap")
	}

	rsp, err = CallReturnBody(
		"org.fedoraproject.FirewallD1",
		"/org/fedoraproject/FirewallD1",
		"org.fedoraproject.FirewallD1.runtimeToPermanent",
		[]any{})

	if err != nil {
		log.Println(err.Error())
	} else {
		log.Println("Firewall: runtime to permanent")
	}

	rsp, err = Call("com.novus.ns",
		"/com/novus/ns",
		"com.novus.ns.snmp.Reset",
		[]any{})

	if err != nil {
		log.Println(err.Error())
	} else {
		log.Println("SNMP: configuration reset")
	}

	rsp, err = Call("com.novus.ns",
		"/com/novus/ns",
		"com.novus.ns.accounts.SetupDefaultUser",
		[]any{})

	if err != nil {
		log.Println(err.Error())
	} else {
		log.Println("Accounts: Default user setup")
	}

	return nil

}
