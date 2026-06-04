/*
Copyright © 2026 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"log"

	"github.com/jowens25/ns/ns/lib"
	"github.com/spf13/cobra"
)

var termCmd = &cobra.Command{
	Use:   "term",
	Short: "start a terminal for the given user",

	Run: func(cmd *cobra.Command, args []string) {

		if err := lib.StartTerminalProxy(); err != nil {
			log.Println(err.Error())
		}

	},
}

func init() {
	rootCmd.AddCommand(termCmd)

}
