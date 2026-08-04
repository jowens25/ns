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
var resetCmd = &cobra.Command{
	Use:   "reset",
	Short: "factory reset system configuration",
	Run: func(cmd *cobra.Command, args []string) {
		cmd.SilenceUsage = true
		_, err := lib.CallReturnBody("com.novus.ns", "/com/novus/ns", "com.novus.ns.pam.ResetDefaultConfig", []any{})

		if err != nil {
			fmt.Println(err.Error())
		} else {
			fmt.Println("System configuration reset")
		}

	},
}

func init() {
	rootCmd.AddCommand(resetCmd)

}
