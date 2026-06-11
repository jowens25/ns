package dbus

import (
	"fmt"

	"github.com/jowens25/ns/ns/lib"
	"github.com/spf13/cobra"
)

var isDebug bool

func Export() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "export",
		Short: "export interfaces on system bus",
		RunE: func(cmd *cobra.Command, args []string) error {
			if isDebug {
				lib.DEBUG = true
				fmt.Println("DEBUGGING NO AUTH CHECKS")
			}
			lib.StartDbusServer()
			return nil
		},
	}
	cmd.Flags().BoolVarP(&isDebug, "debug", "d", false, "ignore auth checks")

	return cmd
}

// func SeeActions() *cobra.Command {
// 	cmd := &cobra.Command{
// 		Use:   "actions",
// 		Short: "check user actions",
// 		RunE: func(cmd *cobra.Command, args []string) error {

// 			conn, _ := dbus.SystemBus()

// 			actions, _ := lib.EnumerateActions(dbus.Sender(conn.Names()[0]))

// 			for _, a := range actions {
// 				fmt.Println(a.Action_id)
// 			}

// 			return nil
// 		},
// 	}
// 	return cmd
// }

// func Test() *cobra.Command {
// 	cmd := &cobra.Command{
// 		Use:   "test",
// 		Short: "test dbus functions",
// 		RunE: func(cmd *cobra.Command, args []string) error {

// 			conn, _ := dbus.SystemBus()

// 			//actions, _ := lib.EnumerateActions(dbus.Sender(conn.Names()[0]))
// 			fmt.Println(lib.GetConnectionCredentials(conn))

// 			return nil
// 		},
// 	}
// 	return cmd
// }

var Dbus = &cobra.Command{
	Use:   "dbus",
	Short: "manage dbus",
}

func init() {
	Dbus.AddCommand(Export())
	//Dbus.AddCommand(SeeActions())
	//Dbus.AddCommand(Test())
}
