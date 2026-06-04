/*
Copyright © 2026 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"github.com/spf13/cobra"
)

// journalCmd represents the stop command
var journalCmd = &cobra.Command{
	Use: "journal",

	Run: func(cmd *cobra.Command, args []string) {

		//lib.TestJournal()

	},
}

func init() {
	rootCmd.AddCommand(journalCmd)

}
