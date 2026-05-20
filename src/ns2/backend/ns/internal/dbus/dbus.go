package dbus

import (
	"fmt"

	"github.com/godbus/dbus/v5"
	"github.com/jowens25/ns/ns/lib"
	"github.com/spf13/cobra"
)

func Export() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "export",
		Short: "export interfaces on system bus",
		RunE: func(cmd *cobra.Command, args []string) error {
			lib.StartDbus()
			return nil
		},
	}
	return cmd
}

func TryClient() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "try",
		Short: "try client ...",
		RunE: func(cmd *cobra.Command, args []string) error {
			//lib.Userinit(0)
			return nil
		},
	}
	return cmd
}

func MakeConn() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "con",
		Short: "make and store conn",
		RunE: func(cmd *cobra.Command, args []string) error {

			//lib.ConnectAs(args[0])

			//lib.CreateConnection()

			return nil
		},
	}
	return cmd
}

func SeeActions() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "actions",
		Short: "check user actions",
		RunE: func(cmd *cobra.Command, args []string) error {

			conn, _ := dbus.SystemBus()

			actions, _ := lib.EnumerateActions(dbus.Sender(conn.Names()[0]))

			for _, a := range actions {
				fmt.Println(a.Action_id)
			}

			return nil
		},
	}
	return cmd
}

func Test() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "test",
		Short: "test dbus functions",
		RunE: func(cmd *cobra.Command, args []string) error {

			conn, _ := dbus.SystemBus()

			//actions, _ := lib.EnumerateActions(dbus.Sender(conn.Names()[0]))
			fmt.Println(lib.GetConnectionCredentials(conn))
			var res1 []any

			err := lib.MyCall(conn, "org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager/Devices/2", "org.freedesktop.NetworkManager.Device.GetAppliedConnection", 0, "u", 0).Store(res1)
			if err != nil {
				fmt.Println(err.Error())
			}
			fmt.Println(res1)

			return nil
		},
	}
	return cmd
}

var Dbus = &cobra.Command{
	Use:   "dbus",
	Short: "manage dbus",
}

func init() {
	Dbus.AddCommand(Export())
	Dbus.AddCommand(TryClient())
	Dbus.AddCommand(MakeConn())
	Dbus.AddCommand(SeeActions())
	Dbus.AddCommand(Test())
}
