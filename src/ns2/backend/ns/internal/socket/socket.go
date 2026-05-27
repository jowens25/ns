package socket

import (
	"github.com/jowens25/ns/ns/lib"
	"github.com/spf13/cobra"
)

func Listen() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "listen",
		Short: "listen to our socket mux",

		RunE: func(cmd *cobra.Command, args []string) error {

			lib.SocketListen()

			return nil
		},
	}

	cmd.Flags().Bool("ws", false, "make ws bridge")

	return cmd
}

var Socket = &cobra.Command{
	Use:   "socket",
	Short: "mess 'round wit sockets",
}

func init() {

	Socket.AddCommand(Listen())

}
