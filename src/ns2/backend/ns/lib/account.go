package lib

import (
	"fmt"
	"os/user"
	"slices"
	"strconv"
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
	if err := KillAllUserProcesses(username); err != nil {
		return err
	}
	return runCmd("userdel", username, "-rf")
}

func KillAllUserProcesses(username string) error {

	// ignoring errors here for now

	runCmd("pkill", "-KILL", "-u", username)

	return nil
}

func MakeNewAdmin(username string, password string) error {

	err := runCmd("useradd",

		"-N",
		"-g",
		"nsadmin",
		"-G",
		"nsuser,nsadmin",
		"--shell",
		"/bin/bash",
		"-m",
		username)

	if err != nil {
		return err
	}

	err = ChangePassword(username, password)

	if err != nil {
		return err
	}

	return nil

}

func ChangePassword(username string, password string) error {

	_, err := user.Lookup(username)
	if err == nil {
		if err := KillAllUserProcesses(username); err != nil {
			return err
		}
	}

	in := fmt.Sprintf("%s:%s\n", username, password)

	err = runCmdWithStdin(in, "chpasswd")
	if err != nil {
		return err
	}
	return nil

}

func GetNumberOfAdmins() (int, error) {

	admins, err := getAdmins()

	if err != nil {
		return -1, err
	}

	return len(admins), nil

}

func IsAdmin(username string) (bool, error) {

	u, err := user.Lookup(username)
	if err != nil {
		return false, err
	}

	groups, err := u.GroupIds()
	if err != nil {
		return false, err
	}

	if slices.Contains(groups, ADMIN_GROUP) {
		return true, nil
	}
	return false, nil
}

func IsUser(username string) (bool, error) {

	u, err := user.Lookup(username)
	if err != nil {
		return false, err
	}

	groups, err := u.GroupIds()
	if err != nil {
		return false, err
	}

	if slices.Contains(groups, USER_GROUP) {
		return true, nil
	}
	return false, nil
}

// this needs to run as root...
func MakeNewUser(username string, password string) error {

	err := runCmd(
		"useradd",

		"-N",
		"-g",
		"nsuser",
		"-G",
		"nsuser",
		"--shell",
		"/bin/bash",
		"-m",
		username)

	if err != nil {
		return err
	}

	return ChangePassword(username, password)

}

func getAdmins() ([]string, error) {
	lines, err := GetFileLines("/etc/group")
	if err != nil {
		return []string{}, err
	}
	for _, line := range lines {
		if strings.HasPrefix(line, ADMIN_GROUP) {
			fields := strings.Split(line, ":")
			if len(fields[3]) > 0 {
				return strings.Split(strings.Trim(fields[3], "\n"), ","), nil
			}

		}
	}

	return nil, err
}

func getUsers() ([]string, error) {
	lines, err := GetFileLines("/etc/group")
	if err != nil {
		return nil, err
	}
	for _, line := range lines {
		if strings.HasPrefix(line, USER_GROUP) {
			fields := strings.Split(line, ":")

			if len(fields[3]) > 0 {
				return strings.Split(strings.Trim(fields[3], "\n"), ","), nil
			}

		}
	}

	return nil, err
}

func getUserAndAdmins() ([]map[string]string, error) {
	users, err := getUsers()
	if err != nil {
		return nil, err
	}

	admins, err := getAdmins()
	if err != nil {
		return nil, err
	}
	allUsers := []map[string]string{}

	if len(admins) > 0 {

		for _, a := range admins {
			idx := slices.Index(users, a)
			if idx != -1 {
				users = slices.Delete(users, idx, idx+1)
			}

			ll, err := GetLastLogin(a)
			if err != nil {
				fmt.Println(err.Error())
				return allUsers, err
			}

			allUsers = append(allUsers, map[string]string{"Groups": "admin", "Username": a, "login": ll})
		}
	}

	if len(users) > 0 {
		for _, u := range users {

			ll, err := GetLastLogin(u)
			if err != nil {
				fmt.Println(err.Error())

				return allUsers, err
			}

			allUsers = append(allUsers, map[string]string{"Groups": "user", "Username": u, "login": ll})

		}
	}

	return allUsers, nil
}

func ListAccounts() {

	accounts, err := getUserAndAdmins()
	if err != nil {
		fmt.Println(err.Error())
	}

	fmt.Println(len(accounts))

	for k, a := range accounts {
		fmt.Println(k, a)
	}

}

func GetLastLogin(username string) (string, error) {

	// Look up user by username
	u, err := user.Lookup(username)
	if err != nil {
		return "", fmt.Errorf("user.Lookup: %s", err.Error())
		//log.Printf("Could not find user: %s", err)
	}

	uid, err := strconv.ParseUint(u.Uid, 10, 32)

	if err != nil {
		return "", fmt.Errorf("strconv.ParseUint: %s", err.Error())
	}

	path, err := Call("org.freedesktop.login1", "/org/freedesktop/login1", "org.freedesktop.login1.Manager.GetUser", []any{uint32(uid)})
	if err != nil {
		return "Not logged in", nil
	}

	if p, ok := path.(dbus.ObjectPath); ok {
		ts, err := Call("org.freedesktop.login1", p, "org.freedesktop.DBus.Properties.Get", []any{"org.freedesktop.login1.User", "Timestamp"})

		if err != nil {

			return "", fmt.Errorf("Call -> GetProp: %s", err.Error())
		}

		ts64, _ := ts.(uint64)

		ts64 = ts64 / 1000000

		tm := time.Unix(int64(ts64), 0)

		fmt.Println(ts64)

		return fmt.Sprintf(tm.Format("2006-01-02 15:04:05")), nil
	}

	return "", fmt.Errorf("invalid path object")

}
