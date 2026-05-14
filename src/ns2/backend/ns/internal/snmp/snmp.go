package snmp

import (
	"fmt"

	"github.com/jowens25/ns/ns/lib"
	"github.com/spf13/cobra"
)

var Snmp = &cobra.Command{
	Use:   "snmp",
	Short: "manage snmpd",
}

func Reset() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "reset",
		Short: "reset snmp config to default",
		RunE: func(cmd *cobra.Command, args []string) error {

			fmt.Println(lib.CallNovusService("snmp.ResetSnmp", []any{}))

			return nil
		},
	}
	return cmd
}

func Test() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "test",
		Short: "test snmp daemon",
		RunE: func(cmd *cobra.Command, args []string) error {

			fmt.Println(lib.CallNovusService("snmp.TestSnmp", []any{}))

			return nil
		},
	}
	//cmd.Flags().Int("port", 8080, "port to listen on")
	return cmd
}

func init() {
	Snmp.AddCommand(Reset())
	Snmp.AddCommand(Test())
}
