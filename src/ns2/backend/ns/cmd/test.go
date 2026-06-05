/*
Copyright © 2026 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// stopCmd represents the stop command
var testCmd = &cobra.Command{
	Use:   "test",
	Args:  cobra.ExactArgs(1),
	Short: "test entry point",

	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("test called")

		//lib.ServeAssets()
		//pid, err := lib.CallMakeTerminal(args[0])
		//
		//if err != nil {
		//	log.Println(err.Error())
		//}
		//
		//fmt.Println(pid)

	},
}

func init() {
	rootCmd.AddCommand(testCmd)

}
