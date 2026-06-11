/*
Copyright © 2026 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"os"

	"github.com/jowens25/ns/ns/internal/account"
	"github.com/jowens25/ns/ns/internal/bridge"
	"github.com/jowens25/ns/ns/internal/dbus"
	"github.com/jowens25/ns/ns/internal/snmp"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "ns",
	Short: "ns2 interface and backend layer",
	Long:  `ns is a set of tools that help you configure linux systems.`,
}

func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func init() {
	rootCmd.CompletionOptions.DisableDefaultCmd = true

	rootCmd.AddCommand(dbus.Dbus)
	rootCmd.AddCommand(snmp.Snmp)
	rootCmd.AddCommand(account.Account)
	rootCmd.AddCommand(bridge.Bridge)
	//rootCmd.AddCommand(socket.Socket)

}

func Root() *cobra.Command { return rootCmd }
