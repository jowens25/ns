package account

import (
	"github.com/jowens25/ns/ns/lib"
	"github.com/spf13/cobra"
)

var Account = &cobra.Command{
	Use:   "account",
	Short: "manage accounts",
}

func Add() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "add",
		Args:  cobra.ExactArgs(1),
		Short: "add users or admins",
		RunE: func(cmd *cobra.Command, args []string) error {
			//println("add account called...")
			//isAdmin, _ := cmd.Flags().GetBool("admin")
			//username := args[0]
			//
			//lib.TestGoPolkit()

			//if isAdmin {
			//
			//	lib.MakeNewAdmin(username)
			//
			//} else {
			//	lib.MakeNewUser(username)
			//}

			return nil
		},
	}
	cmd.Flags().BoolP("admin", "a", false, "make an admin account")
	return cmd
}

func Remove() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "add",
		Args:  cobra.ExactArgs(1),
		Short: "add users or admins",
		RunE: func(cmd *cobra.Command, args []string) error {
			//println("add account called...")
			//isAdmin, _ := cmd.Flags().GetBool("admin")
			//username := args[0]
			//
			//lib.TestGoPolkit()

			//if isAdmin {
			//
			//	lib.MakeNewAdmin(username)
			//
			//} else {
			//	lib.MakeNewUser(username)
			//}

			return nil
		},
	}
	cmd.Flags().BoolP("admin", "a", false, "make an admin account")
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
	Account.AddCommand(List())

}
