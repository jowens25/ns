package lib

import (
	"fmt"
	"io"
	"log"
	"net"
)

func SocketListen() {
	socketPath := "/var/lib/ns/ns-serial-mux.sock"

	// Connect to the socket
	conn, err := net.Dial("unix", socketPath)
	if err != nil {
		log.Fatal("dial error:", err)
	}
	defer conn.Close()

	// Create a buffer to store incoming data
	buf := make([]byte, 1024)

	// 2. Loop continuously to read the stream
	for {
		n, err := conn.Read(buf)
		if err != nil {
			if err == io.EOF {
				fmt.Println("Connection closed by the remote side.")
				break
			}
			log.Printf("Read error: %v\n", err)
			break
		}

		// Process the data that was just read
		data := buf[:n]
		fmt.Printf("%s", string(data))
	}
}
