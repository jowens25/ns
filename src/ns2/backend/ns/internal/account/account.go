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

		Use:   "add <username> <password>",
		Args:  cobra.ExactArgs(2),
		Short: "add users or admins",
		RunE: func(cmd *cobra.Command, args []string) error {
			cmd.SilenceUsage = true
			if isAdmin {
				rsp, err := lib.Call("com.novus.ns", "/com/novus/ns", "com.novus.ns.accounts.AddAdmin", []any{args[0], args[1]})

				if err != nil {
					return err
				}

				fmt.Println(rsp)

			} else {
				rsp, err := lib.Call("com.novus.ns", "/com/novus/ns", "com.novus.ns.accounts.AddUser", []any{args[0], args[1]})

				if err != nil {
					return err
				}

				fmt.Println(rsp)

			}
			return nil
		},
	}
	cmd.Flags().BoolVarP(&isAdmin, "admin", "a", false, "make an admin account")
	return cmd
}

func Remove() *cobra.Command {

	cmd := &cobra.Command{
		Use:   "rm <username>",
		Args:  cobra.ExactArgs(1),
		Short: "remove users or admins",
		RunE: func(cmd *cobra.Command, args []string) error {
			cmd.SilenceUsage = true
			rsp, err := lib.Call("com.novus.ns", "/com/novus/ns", "com.novus.ns.accounts.Remove", []any{args[0]})

			if err != nil {
				return err
			}

			fmt.Println(rsp)

			return nil
		},
	}
	return cmd
}

func Reset() *cobra.Command {

	cmd := &cobra.Command{
		Use:   "reset",
		Short: "resets the default user",
		RunE: func(cmd *cobra.Command, args []string) error {
			cmd.SilenceUsage = true
			rsp, err := lib.Call("com.novus.ns", "/com/novus/ns", "com.novus.ns.accounts.SetupDefaultUser", nil)

			if err != nil {
				return err
			}

			fmt.Println(rsp)

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
			cmd.SilenceUsage = true
			users, err := lib.Call("com.novus.ns", "/com/novus/ns", "com.novus.ns.accounts.GetUsers", nil)

			if err != nil {
				return err
			}

			for _, u := range users.([]map[string]string) {

				username := u["Username"]
				group := u["Group"]

				fmt.Printf("%s:%s\n", group, username)
			}

			return nil
		},
	}

	return cmd
}

func init() {
	Account.AddCommand(Add())
	Account.AddCommand(Remove())
	Account.AddCommand(List())
	Account.AddCommand(Reset())

}
