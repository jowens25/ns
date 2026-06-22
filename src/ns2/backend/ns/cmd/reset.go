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
	RunE: func(cmd *cobra.Command, args []string) error {
		cmd.SilenceUsage = true
		_, err := lib.CallReturnBody("com.novus.ns", "/com/novus/ns", "com.novus.ns.pam.ResetDefaultConfig", []any{})

		if err != nil {
			return err
		}

		fmt.Println("System configuration reset")

		return nil
	},
}

func init() {
	rootCmd.AddCommand(resetCmd)

}
