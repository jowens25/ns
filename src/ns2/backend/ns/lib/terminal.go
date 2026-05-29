package lib

import (
	"errors"
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"os/exec"
	"os/signal"
	"os/user"
	"syscall"

	"github.com/creack/pty"
)

func CallMakeTerminal(username string) (int, error) {

	if _, err := user.Lookup(username); err != nil {
		return -1, fmt.Errorf("unknown user %q: %w", username, err)
	}

	cmd := exec.Command(
		"sudo",
		"-u", username,
		"ns",
		"term",
	)
	fmt.Println("cmd term called")

	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	err := cmd.Start()
	if err != nil {
		return -1, err
	}

	fmt.Println("start called")

	return cmd.Process.Pid, nil
}

var terminalSocketPath string = "/tmp/terminal.sock"

func StartTerminalProxy() error {
	log.Println("starting terminal proxy...")

	err := os.Remove(terminalSocketPath)
	if !errors.Is(err, os.ErrNotExist) {
		return err
	}

	listener, err := net.Listen("unix", terminalSocketPath)
	if err != nil {
		log.Println(err)
		return err
	}
	defer listener.Close()

	if err := os.Chmod(terminalSocketPath, 0777); err != nil {
		log.Fatal(err)
	}

	go func() {
		for {
			conn, err := listener.Accept()
			if err != nil {
				log.Printf("accept error: %v", err)
				return
			}
			go handleConnection(conn)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop

	log.Println("shutting down terminal proxy listener...")
	listener.Close() // closing the listener is sufficient - Accept() will error and the goroutine exits
	return nil

}

func handleConnection(conn net.Conn) {
	c := exec.Command("bash", "-i", "-l")

	if homeDir, err := os.UserHomeDir(); err == nil {
		c.Dir = homeDir
	}

	// Start the command with a pty.
	ptmx, err := pty.Start(c)
	if err != nil {
		return
	}

	defer func() {
		ptmx.Close()
		c.Process.Kill()
		c.Wait()
		conn.Close()
		os.Remove(terminalSocketPath)
	}()

	errc := make(chan error, 2)
	go func() { _, err := io.Copy(ptmx, conn); errc <- err }()
	go func() { _, err := io.Copy(conn, ptmx); errc <- err }()
	<-errc

	log.Println("shutting down terminal proxy conn...")

}
