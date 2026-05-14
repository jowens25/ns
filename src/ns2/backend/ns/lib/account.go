package lib

import (
	"fmt"
	"log"
	"os/exec"
	"slices"
	"strings"
)

var ADMIN_GROUP string = "nsadmin"
var USER_GROUP string = "nsuser"

func MakeNewAdmin(username string) {

	cmd := exec.Command(
		"useradd",
		"-M",
		"-N",
		"-g",
		"nsadmin",
		"-G",
		"nsuser,nsadmin",
		"--shell",
		"/bin/bash",
		"-d",
		fmt.Sprintf("/home/%s", username),
		username,
	)

	stdoutStderr, err := cmd.CombinedOutput()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("%s\n", stdoutStderr)

}

// this needs to run as root...
func MakeNewUser(username string) {

	cmd := exec.Command(
		"useradd",
		"-M",
		"-N",
		"-g",
		"nsuser",
		"-G",
		"nsuser",
		"--shell",
		"/bin/bash",
		"-d",
		fmt.Sprintf("/home/%s", username),
		username,
	)

	stdoutStderr, err := cmd.CombinedOutput()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("%s\n", stdoutStderr)

}

func getAdmins() []string {
	for _, line := range GetFileLines("/etc/group") {
		if strings.HasPrefix(line, ADMIN_GROUP) {
			fields := strings.Split(line, ":")
			return strings.Split(strings.Trim(fields[3], "\n"), ",")

		}
	}

	return nil
}

func getUsers() []string {
	for _, line := range GetFileLines("/etc/group") {
		if strings.HasPrefix(line, USER_GROUP) {
			fields := strings.Split(line, ":")
			return strings.Split(strings.Trim(fields[3], "\n"), ",")

		}
	}

	return nil
}

func getUserAndAdmins() []string {

	users := getUsers()
	admins := getAdmins()

	var allUsers []string

	for _, a := range admins {
		idx := slices.Index(users, a)
		if idx > 0 {
			users = slices.Delete(users, idx, idx+1)
		}

		allUsers = append(allUsers, a)
	}

	for _, u := range users {

		allUsers = append(allUsers, u)

	}

	return allUsers
}

func ListAccounts() {

	for _, a := range getUserAndAdmins() {
		println(a)
	}

}
