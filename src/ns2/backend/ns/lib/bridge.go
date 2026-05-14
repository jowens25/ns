package lib

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/godbus/dbus/v5"
)

type DbusCall struct {
	Destination string `json:"Destination" binding:"required"` // object
	Path        string `json:"Path" binding:"required"`        // object
	Method      string `json:"Method" binding:"required"`      // call
	Args        []any  `json:"Args"`                           // call
}

func Call(conn *dbus.Conn, call DbusCall) (any, error) {

	var result any
	obj := conn.Object(call.Destination, dbus.ObjectPath(call.Path))

	err := obj.Call(call.Method, 0, call.Args...).Store(&result)
	if err != nil {
		return nil, err
	}
	return result, nil

}

// calls connect call with default:
// com.novus.ns
// /com/novus/ns
func CallNovusService(subinterfaceMethod string, args []any) any {

	return ConnectCall("com.novus.ns", "/com/novus/ns", "com.novus.ns."+subinterfaceMethod, args)

}

func ConnectCall(destination string, path string, method string, args []any) any {

	conn, err := dbus.ConnectSystemBus()

	if err != nil {
		fmt.Fprintln(os.Stderr, "Failed to connect to sys bus:", err)
		os.Exit(1)
	}
	defer conn.Close()
	r, err := Call(conn, DbusCall{Destination: destination, Path: path, Method: method, Args: args})

	if err != nil {
		return err
	}
	return r

}

func callHandler(conn *dbus.Conn) gin.HandlerFunc {
	return func(c *gin.Context) {
		var call DbusCall
		if err := c.ShouldBindJSON(&call); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{
				"error":   "Invalid request format",
				"details": err.Error(),
			})
			fmt.Println(err.Error())
			return
		}

		//log.Println(call)
		res, err := Call(conn, call)
		if err != nil {
			c.JSON(http.StatusOK, map[string]string{"Dbus": err.Error()})
			return
		}

		//log.Println(res)
		c.JSON(http.StatusOK, res)
		return

	}
}

func InitHttpBridge() {

	// opens dbus connection as user
	conn, err := dbus.ConnectSystemBus()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Failed to connect to sys bus:", err)
		os.Exit(1)
	}
	defer conn.Close()

	//gin.SetMode(gin.ReleaseMode)

	r := gin.Default()

	cfg := cors.DefaultConfig()

	cfg.AllowMethods = []string{"POST"}
	cfg.AllowOrigins = []string{"http://localhost"}
	r.SetTrustedProxies([]string{"http://localhost"})

	r.Use(cors.New(cfg))

	r.Use(gin.Recovery())

	r.POST("/call", callHandler(conn)) // POST TO THE BRIDGE IS A Call OR SET

	r.Run("localhost:8080") // offical
}

func CallMakeBridge(username string) int {

	cmd := exec.Command(
		"sudo",
		"-u", username,
		"ns",
		"bridge",
		"make",
	)

	if err := cmd.Start(); err != nil {
		return -1
	}

	return cmd.Process.Pid
}

func CallEndBridge(pid int) {

	cmd := exec.Command(
		"sudo",
		"kill",
		fmt.Sprintf("%d", pid),
	)

	stdoutStderr, err := cmd.CombinedOutput()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("%s\n", stdoutStderr)

}
