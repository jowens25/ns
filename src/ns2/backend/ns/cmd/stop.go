/*
Copyright © 2026 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"

	"github.com/jowens25/ns/ns/lib"
	"github.com/spf13/cobra"
)

// stopCmd represents the stop command
var stopCmd = &cobra.Command{
	Use:   "stop",
	Args:  cobra.ExactArgs(1),
	Short: "stop a systemd service",
	Long:  `this is a shortcut for systemctl stop <name.service>`,
	Run: func(cmd *cobra.Command, args []string) {

		err := lib.Stop(args[0])

		if err != nil {
			fmt.Println(err.Error())
		}

	},
}

func init() {
	rootCmd.AddCommand(stopCmd)

}
