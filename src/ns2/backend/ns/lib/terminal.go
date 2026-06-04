package lib

import (
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

	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	err := cmd.Start()
	if err != nil {
		return -1, err
	}

	return cmd.Process.Pid, nil
}

var terminalSocketPath string = "/tmp/terminal.sock"

func StartTerminalProxy() error {
	log.Println("starting terminal proxy...")

	os.Remove(terminalSocketPath)

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
				continue
			}
			go func() {
				if err := handleConnection(conn); err != nil {
					log.Printf("connection error: %v", err)
				}
			}()
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop

	log.Println("shutting down terminal proxy listener...")
	listener.Close() // closing the listener is sufficient - Accept() will error and the goroutine exits
	return nil

}

func handleConnection(conn net.Conn) error {
	cmd := exec.Command("bash", "-i", "-l")

	// cmd.SysProcAttr = &syscall.SysProcAttr{
	// 	Setsid: true, // new session, isolates signals from parent
	// }

	homeDir, err := os.UserHomeDir()
	if err != nil {
		return err
	}
	cmd.Dir = homeDir

	// Start the command with a pty.
	ptmx, err := pty.Start(cmd)
	if err != nil {
		return err
	}

	defer func() {
		ptmx.Close()
		//cmd.Process.Kill()
		//cmd.Wait()
		conn.Close()
	}()

	errc := make(chan error, 2)
	go func() { _, err := io.Copy(ptmx, conn); errc <- err }()
	go func() { _, err := io.Copy(conn, ptmx); errc <- err }()
	<-errc

	log.Println("shutting down terminal proxy conn...")
	return nil

}
