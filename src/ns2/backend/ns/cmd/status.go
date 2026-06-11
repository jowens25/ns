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
var statusCmd = &cobra.Command{
	Use:   "status <name.service>",
	Short: "status of a systemd service",
	Long:  `this is a shortcut for systemctl status <name.service>`,
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {

		fmt.Println(lib.GetUnitStatus(args[0]))
	},
}

func init() {
	rootCmd.AddCommand(statusCmd)

}
