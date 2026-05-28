package account

import (
	"fmt"

	"github.com/jowens25/ns/ns/lib"
	"github.com/spf13/cobra"
)

var Account = &cobra.Command{
	Use:   "account",
	Short: "manage accounts",
}

func Add() *cobra.Command {
	var isAdmin bool

	cmd := &cobra.Command{
		Use:   "add",
		Args:  cobra.ExactArgs(2),
		Short: "add users or admins",
		RunE: func(cmd *cobra.Command, args []string) error {
			if isAdmin {
				err := lib.MakeNewAdmin(args[0], args[1])
				if err != nil {
					fmt.Println(err.Error())
				}
			} else {
				err := lib.MakeNewUser(args[0], args[1])
				if err != nil {
					fmt.Println(err.Error())
				}
			}
			return nil
		},
	}
	cmd.Flags().BoolVarP(&isAdmin, "admin", "a", false, "make an admin account")
	return cmd
}

func Remove() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "remove",
		Args:  cobra.ExactArgs(1),
		Short: "remove users or admins",
		RunE: func(cmd *cobra.Command, args []string) error {

			fmt.Println("removing...")
			err := lib.RemoveUser(args[0])
			if err != nil {
				fmt.Println(err.Error())
			}

			return nil
		},
	}
	return cmd
}

func List() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "ls",
		Short: "list accounts",
		RunE: func(cmd *cobra.Command, args []string) error {
			lib.ListAccounts()
			return nil
		},
	}

	return cmd
}

func init() {
	Account.AddCommand(Add())
	Account.AddCommand(Remove())
	Account.AddCommand(List())

}
