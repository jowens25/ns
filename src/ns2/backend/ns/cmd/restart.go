/*
Copyright © 2026 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"

	"github.com/jowens25/ns/ns/lib"
	"github.com/spf13/cobra"
)

// statusCmd represents the status command
var restartCmd = &cobra.Command{
	Use:   "restart <name.service>",
	Short: "restart a systemd service",
	Long:  `this is a shortcut for systemctl restart <name.service>`,
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {

		err := lib.Restart(args[0])

		if err != nil {
			fmt.Println(err.Error())
		}
	},
}

func init() {
	rootCmd.AddCommand(restartCmd)

}
