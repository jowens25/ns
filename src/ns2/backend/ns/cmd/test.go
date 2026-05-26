/*
Copyright © 2026 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"
	"os"

	"github.com/godbus/dbus/v5"
	"github.com/jowens25/ns/ns/lib"
	"github.com/spf13/cobra"
)

// testCmd represents the test command
var testCmd = &cobra.Command{
	Use:   "test",
	Short: "A brief description of your command",

	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("test called")

		conn, err := dbus.SystemBus()
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to connect to system bus: %v\n", err)
			os.Exit(1)
		}
		defer conn.Close()

		var thisCall lib.DbusCall
		thisCall.Destination = "org.freedesktop.NetworkManager"
		thisCall.Path = "/org/freedesktop/NetworkManager/Devices/2"
		thisCall.Method = "org.freedesktop.NetworkManager.Device.GetAppliedConnection"

		thisCall.Args = []any{uint32(0)}

		obj := conn.Object(thisCall.Destination, thisCall.Path)

		dbuscall := obj.Call(thisCall.Method, 0, thisCall.Args...)

		fmt.Println(dbuscall.Body)

	},
}

func init() {
	rootCmd.AddCommand(testCmd)

}
