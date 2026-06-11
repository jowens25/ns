package lib

import (
	"context"
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"os/signal"
)

func SocketListen(socketPath string) {
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()

	conn, err := net.Dial("unix", socketPath)
	if err != nil {
		log.Fatal("dial error:", err)
	}
	defer conn.Close()

	// Run the read loop in a goroutine
	done := make(chan struct{})
	go func() {
		defer close(done)
		buf := make([]byte, 1024)
		for {
			n, err := conn.Read(buf)
			if err != nil {
				if err == io.EOF {
					fmt.Println("Connection closed by the remote side.")
				} else {
					log.Printf("Read error: %v\n", err)
				}
				return
			}
			fmt.Printf("%s", string(buf[:n]))
		}
	}()

	// Block until Ctrl+C or the read loop finishes
	select {
	case <-ctx.Done():
		fmt.Println("\nInterrupted, closing connection...")
		conn.Close() // unblocks conn.Read in the goroutine
	case <-done:
		// remote closed naturally
	}

	<-done
}
