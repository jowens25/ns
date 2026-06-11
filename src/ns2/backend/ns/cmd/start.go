/*
Copyright © 2026 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"

	"github.com/jowens25/ns/ns/lib"
	"github.com/spf13/cobra"
)

var startCmd = &cobra.Command{
	Use:   "start <name.service>",
	Args:  cobra.ExactArgs(1),
	Short: "start a systemd service",
	Long:  `this is a shortcut for systemctl start <name.service>`,
	Run: func(cmd *cobra.Command, args []string) {
		err := lib.Start(args[0])

		if err != nil {
			fmt.Println(err.Error())
		}
	},
}

func init() {
	rootCmd.AddCommand(startCmd)

}
