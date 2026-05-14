package lib

import (
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
	}

	return strings.Split(string(content), "\n")
}

func SetFileLines(path string, lines []string) {
	os.WriteFile(path, []byte(strings.Join(lines, "\n")), 0644)
}

func runCmd(cmd string, args ...string) {

	exec.Command(cmd, args...).Run()

}

func HasAll(line string, elements []string) bool {

	for _, e := range elements {

		if !strings.Contains(line, e) {
			return false
		}

	}
	return true
}
