package lib

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
)

// returns slice of file content split with \n
func GetFileLines(path string) ([]string, error) {

	content, err := os.ReadFile(path)
	if err != nil {
		log.Println("get file lines: failed to read: ", path)
		log.Println(err)

		return []string{}, err
	}

	return strings.Split(string(content), "\n"), nil
}

func SetFileLines(path string, lines []string) error {
	err := os.WriteFile(path, []byte(strings.Join(lines, "\n")), 0644)
	if err != nil {
		return err
	}
	return nil
}

func runCmd(cmd string, args ...string) error {

	out, err := exec.Command(cmd, args...).CombinedOutput()

	if err != nil {

		return fmt.Errorf("runCmd failed callling: %s with: %s -> out: %s", cmd, err.Error(), string(out))
	}

	return nil

}

func runCmdWithStdin(stdin string, cmd string, args ...string) error {
	c := exec.Command(cmd, args...)
	c.Stdin = strings.NewReader(stdin) // e.g. "username:newpassword\n"

	out, err := c.CombinedOutput()
	if err != nil {
		return fmt.Errorf("runCmdWithStdin failed: %s -> out: %s", err, string(out))
	}
	return nil
}

func HasAll(line string, elements []string) bool {

	for _, e := range elements {

		if !strings.Contains(line, e) {
			return false
		}

	}
	return true
}
