/*
Copyright © 2026 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"

	"github.com/msteinert/pam"
	"github.com/spf13/cobra"
)

// journalCmd represents the stop command
var pamCmd = &cobra.Command{
	Use: "pam",

	Run: func(cmd *cobra.Command, args []string) {

		user := args[0]
		password := args[1]

		t, err := pam.StartFunc("login", user, func(s pam.Style, msg string) (string, error) {
			switch s {
			case pam.PromptEchoOff:
				return password, nil
			case pam.PromptEchoOn:
				return user, nil
			}
			return "", nil
		})

		if err != nil {

			fmt.Println(err.Error())
		}

		if err = t.Authenticate(0); err != nil {
			fmt.Println("auth error: ", err.Error())

		}

		if err = t.AcctMgmt(0); err != nil {
			fmt.Println("acctmgnt error: ", err.Error())

		}

		if err = t.OpenSession(0); err != nil {
			fmt.Println("open sess error: ", err.Error())

		}
		t.CloseSession(0)

		fmt.Println("END??")

	},
}

func init() {
	rootCmd.AddCommand(pamCmd)

}
