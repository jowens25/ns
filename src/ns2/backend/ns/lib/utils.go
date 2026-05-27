package lib

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
)

// returns slice of file content split with \n
func GetFileLines(path string) []string {

	content, err := os.ReadFile(path)
	if err != nil {
		log.Println("get file lines: failed to read: ", path)
		log.Println(err)

		return []string{}
	}

	return strings.Split(string(content), "\n")
}

func SetFileLines(path string, lines []string) {
	os.WriteFile(path, []byte(strings.Join(lines, "\n")), 0644)
}

func runCmd(cmd string, args ...string) error {

	out, err := exec.Command(cmd, args...).CombinedOutput()

	if err != nil {

		return fmt.Errorf("run Cmd failed with: %s -> out: %s", err.Error(), string(out))
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
