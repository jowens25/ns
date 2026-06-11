package bridge

import (
	"github.com/jowens25/ns/ns/lib"
	"github.com/spf13/cobra"
)

func MakeBridge() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "make",
		Short: "make bridge",

		RunE: func(cmd *cobra.Command, args []string) error {

			lib.StartBridgeProxy()

			return nil
		},
	}

	return cmd
}

var Bridge = &cobra.Command{
	Use:   "bridge",
	Short: "manage websocket bridge",
}

func init() {

	Bridge.AddCommand(MakeBridge())

}
