package lib

import (
	"fmt"
	"os"

	"github.com/godbus/dbus/v5"
	"github.com/godbus/dbus/v5/introspect"
)

func StartDbus() {
	conn, err := dbus.SystemBus()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to connect to system bus: %v\n", err)
		os.Exit(1)
	}
	defer conn.Close()

	reply, err := conn.RequestName("com.novus.ns", dbus.NameFlagDoNotQueue)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to request name: %v\n", err)
		os.Exit(1)
	}
	if reply != dbus.RequestNameReplyPrimaryOwner {
		fmt.Fprintf(os.Stderr, "Name already taken\n")
		os.Exit(1)
	}
	// export interfaces
	snmp := &SnmpInterface{}
	snmp.conn = conn
	err = conn.Export(snmp, "/com/novus/ns", "com.novus.ns.snmp")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to export SnmpInterface: %v\n", err)
		os.Exit(1)
	}

	bridge := NewBridgeInterface()
	bridge.conn = conn
	err = conn.Export(bridge, "/com/novus/ns", "com.novus.ns.bridge")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to export bridgeInterface: %v\n", err)
		os.Exit(1)
	}

	// Export the Properties interface for bridge
	err = conn.Export(bridge, "/com/novus/ns", "org.freedesktop.DBus.Properties")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to export Properties interface: %v\n", err)
		os.Exit(1)
	}

	pam := &PamInterface{}
	err = conn.Export(pam, "/com/novus/ns", "com.novus.ns.pam")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to export PamInterface: %v\n", err)
		os.Exit(1)
	}

	account := &AccountInterface{}
	err = conn.Export(account, "/com/novus/ns", "com.novus.ns.account")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to export AccountInterface: %v\n", err)
		os.Exit(1)
	}

	// Add introspection support
	node := &introspect.Node{
		Name: "/com/novus/ns",
		Interfaces: []introspect.Interface{
			introspect.IntrospectData,
			{
				Name:    "com.novus.ns.bridge",
				Methods: introspect.Methods(bridge),
				Properties: []introspect.Property{
					{
						Name:   "pid",
						Type:   "u",
						Access: "read",
					},
				},
			},
			{
				Name:       "com.novus.ns.snmp",
				Methods:    introspect.Methods(snmp),
				Properties: nil,
			},
			{
				Name:       "com.novus.ns.pam",
				Methods:    introspect.Methods(pam),
				Properties: nil,
			},
			{
				Name:       "com.novus.ns.accounts",
				Methods:    introspect.Methods(account),
				Properties: nil,
			},
		},
	}
	err = conn.Export(introspect.NewIntrospectable(node), "/com/novus/ns", "org.freedesktop.DBus.Introspectable")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to export introspectable: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Starting ns service... com.novus.ns")
	// Wait forever
	select {}
}

func TryClient() {
	conn, err := dbus.ConnectSystemBus()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Failed to connect to sys bus:", err)
		os.Exit(1)
	}
	defer conn.Close()

	var s any
	obj := conn.Object("com.novus.ns", "/com/novus/ns")
	err = obj.Call("com.novus.ns.bridge.Call", 0,
		"jowens",
		"org.freedesktop.NetworkManager",
		"/org/freedesktop/NetworkManager",
		"org.freedesktop.NetworkManager.GetDeviceByIpIface",
		"enp3s0",
		//[]any{dbus.MakeVariant("enp3s0")},
	).Store(&s)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Failed to call bridge function", err)
		os.Exit(1)
	}

	fmt.Println("Result from calling call function on bridge interface:")
	fmt.Println(s)
}
