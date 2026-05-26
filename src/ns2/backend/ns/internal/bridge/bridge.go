package bridge

import (
	"github.com/jowens25/ns/ns/lib"
	"github.com/spf13/cobra"
)

func MakeBridge() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "make",
		Short: "make bridge <port> <handle func>",

		RunE: func(cmd *cobra.Command, args []string) error {

			isWs, _ := cmd.Flags().GetBool("ws")

			if isWs {
				//lib.InitWebSocketBridge()
			} else {
				lib.StartBridgeProxy("none")
			}

			return nil
		},
	}

	cmd.Flags().Bool("ws", false, "make ws bridge")

	return cmd
}

var Bridge = &cobra.Command{
	Use:   "bridge",
	Short: "manage websocket bridge",
}

func init() {

	Bridge.AddCommand(MakeBridge())

}
