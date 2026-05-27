package lib

import (
	"fmt"
	"slices"
	"strings"
	"time"

	"github.com/godbus/dbus/v5"
)

var ADMIN_GROUP string = "nsadmin"
var USER_GROUP string = "nsuser"

type User struct {
	Username string `json:"Username"`
	Group    string `json:"Group"`
	Last     string `json:"Last"`
}

func RemoveUser(username string) error {
	return runCmd("userdel", username, "-rf")
}

func MakeNewAdmin(username string) error {

	return runCmd("useradd",
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
		username)

}

// this needs to run as root...
func MakeNewUser(username string) error {

	return runCmd(
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
		username)

}

func getAdmins() []string {
	for _, line := range GetFileLines("/etc/group") {
		if strings.HasPrefix(line, ADMIN_GROUP) {
			fields := strings.Split(line, ":")
			if len(fields[3]) > 0 {
				return strings.Split(strings.Trim(fields[3], "\n"), ",")
			}

		}
	}

	return nil
}

func getUsers() []string {
	for _, line := range GetFileLines("/etc/group") {
		if strings.HasPrefix(line, USER_GROUP) {
			fields := strings.Split(line, ":")

			if len(fields[3]) > 0 {
				return strings.Split(strings.Trim(fields[3], "\n"), ",")
			}

		}
	}

	return nil
}

func getUserAndAdmins() []string {

	users := getUsers()
	admins := getAdmins()

	var allUsers []string

	if len(admins) > 0 {

		for _, a := range admins {
			idx := slices.Index(users, a)
			if idx != -1 {
				users = slices.Delete(users, idx, idx+1)
			}

			allUsers = append(allUsers, a)
		}
	}

	if len(users) > 0 {
		for _, u := range users {

			allUsers = append(allUsers, u)

		}
	}

	return allUsers
}

func ListAccounts() {

	accounts := getUserAndAdmins()

	fmt.Println(len(accounts))

	for _, a := range accounts {
		fmt.Println(a)
	}

}

func GetLastLogin(uid uint32) (string, error) {

	path, err := Call("org.freedesktop.login1", "/org/freedesktop/login1", "org.freedesktop.login1.Manager.GetUser", []any{uid})
	if err != nil {
		return "", err
	}

	if p, ok := path.(dbus.ObjectPath); ok {
		ts, err := Call("org.freedesktop.login1", p, "org.freedesktop.DBus.Properties.Get", []any{"org.freedesktop.login1.User", "Timestamp"})
		ts64, _ := ts.(uint64)
		if err != nil {
			return "", err
		}

		ts64 = ts64 / 1000000

		tm := time.Unix(int64(ts64), 0)

		fmt.Println(ts64)

		return fmt.Sprintf(tm.Format("2006-01-02 15:04:05")), nil
	}

	return "", fmt.Errorf("invalid path object")

}
