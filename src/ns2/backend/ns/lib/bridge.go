package lib

import (
	"encoding/hex"
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"os/exec"
	"os/signal"
	"os/user"
	"strconv"
	"syscall"
)

func CallMakeBridge(username string) (int, error) {

	if _, err := user.Lookup(username); err != nil {
		return -1, fmt.Errorf("unknown user %q: %w", username, err)
	}

	cmd := exec.Command(
		"sudo",
		"-u", username,
		"ns",
		"bridge",
		"make",
	)

	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	err := cmd.Start()
	if err != nil {
		return -1, err
	}

	return cmd.Process.Pid, nil
}

func callClose(pid int) error {

	cmd := exec.Command(
		"sudo",
		"kill",
		fmt.Sprintf("%d", pid),
	)

	_, err := cmd.CombinedOutput()
	if err != nil {
		return err
	}
	return nil
}

func StartBridgeProxy() error {
	log.Println("starting bridge proxy...")

	listener, err := net.Listen("tcp", "localhost:3000")
	if err != nil {
		return err
	}

	go func() {
		for {
			clientConn, err := listener.Accept()
			if err != nil {
				return
			}
			go proxyConn(clientConn)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop

	log.Println("shutting down bridge proxy listener...")
	listener.Close() // closing the listener is sufficient - Accept() will error and the goroutine exits
	return nil
}

func proxyConn(client net.Conn) {

	defer client.Close()

	dbusPath := "/var/run/dbus/system_bus_socket"

	dbusSocket, err := net.Dial("unix", dbusPath)
	if err != nil {
		log.Println(err)
		return
	}
	defer dbusSocket.Close()

	uid := os.Getuid()
	hexUID := hex.EncodeToString([]byte(strconv.Itoa(uid)))

	dbusSocket.Write([]byte("\x00"))
	fmt.Fprintf(dbusSocket, "AUTH EXTERNAL %s\r\n", hexUID)
	okLine := readLine(dbusSocket)
	fmt.Fprintf(dbusSocket, "BEGIN\r\n")

	client.Read(make([]byte, 1)) // null byte
	readLine(client)             // AUTH EXTERNAL ...
	client.Write([]byte(okLine)) // send real OK back
	readLine(client)             // BEGIN

	fmt.Printf("listening to %d on %s\n", uid, client.LocalAddr().String())

	errc := make(chan error, 2)
	go func() { _, err := io.Copy(dbusSocket, client); errc <- err }()
	go func() { _, err := io.Copy(client, dbusSocket); errc <- err }()
	<-errc
}

func readLine(conn net.Conn) string {
	var line []byte
	buf := make([]byte, 1)
	for {
		conn.Read(buf)
		line = append(line, buf[0])
		if len(line) >= 2 && line[len(line)-2] == '\r' && line[len(line)-1] == '\n' {
			return string(line)
		}
	}
}
