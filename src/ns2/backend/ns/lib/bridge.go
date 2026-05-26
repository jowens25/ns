package lib

import (
	"encoding/hex"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"os/user"
	"strconv"
	"sync"
	"syscall"

	"github.com/godbus/dbus/v5"
	"github.com/gorilla/websocket"
)

type DbusCall struct {
	Destination string          `json:"Destination" binding:"required"` // object
	Path        dbus.ObjectPath `json:"Path" binding:"required"`        // object
	Method      string          `json:"Method" binding:"required"`      // call
	Args        []any           `json:"Args"`                           // call
	Signature   string          `json:"Signature" binding:"required"`
	Returns     string          `json:"Returns" binding:"required"`
}

// swtich type assert then iterate and pack into map[string]string
func ParseWithReturnType(returnType string, rsp any) any {

	switch returnType {

	case "aa{sv}":
		result := []map[string]string{}
		val := rsp.(dbus.Variant).Value()
		list, ok := val.([]map[string]dbus.Variant)

		if ok {
			for _, dictEntry := range list {

				temp := map[string]string{}
				for k, v := range dictEntry {

					temp[k] = fmt.Sprintf("%v", v.Value())
				}

				result = append(result, temp)

			}
		}

		return result

	//case "a{sa{sv}}":

	//result := []map[string]map[string]string{}

	default:

		return rsp

	}

}

// returns body, result, err
func MakeDbusCall(conn *dbus.Conn, call DbusCall) (any, any, error) {

	var result any

	obj := conn.Object(call.Destination, call.Path)

	dbuscall := obj.Call(call.Method, 0, call.Args...)
	fmt.Println("dbuscall: ", dbuscall)

	err := dbuscall.Store(&result)

	if err != nil {
		return nil, nil, err
	}
	return dbuscall.Body[0], result, nil

}

//func ParseDbusResponse(response any) any {
//
//
//	if v, ok := response.
//
//	if v, ok := response.(dbus.Variant); ok {
//		return v.Value()
//	}
//
//
//
//	return ""
//
//}

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
		"--ws",
	)

	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	err := cmd.Start()
	if err != nil {
		return -1, err
	}

	return cmd.Process.Pid, nil
}

func callCloseBridge(pid int) error {

	cmd := exec.Command(
		"sudo",
		"kill",
		fmt.Sprintf("%d", pid),
	)

	_, err := cmd.CombinedOutput()
	if err != nil {
		return err
	}
	//fmt.Printf("%s\n", stdoutStderr)
	return nil
}

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		// In production, validate origin properly
		//origin := r.Header.Get("Origin")
		return true //return origin == "http://localhost" || origin == "ws://localhost:8080"
	},
}

type DbusMessage struct {
	Type        string        `json:"type"` // "call", "signal", "get", "set"
	Destination string        `json:"destination,omitempty"`
	Path        string        `json:"path,omitempty"`
	Interface   string        `json:"interface,omitempty"`
	Member      string        `json:"member,omitempty"`
	Args        []interface{} `json:"args,omitempty"`
	RequestID   string        `json:"request_id,omitempty"`
}

type DbusResponse struct {
	RequestID string        `json:"request_id"`
	Success   bool          `json:"success"`
	Result    []interface{} `json:"result,omitempty"`
	Error     string        `json:"error,omitempty"`
}

type Client struct {
	conn     *websocket.Conn
	send     chan []byte
	dbusConn *dbus.Conn
	mu       sync.Mutex
}

// func InitWebSocketBridge() {
// 	mux := http.NewServeMux()
// 	mux.HandleFunc("/bridge", handleWebSocket)

// 	srv := &http.Server{
// 		Addr:    "localhost:3000",
// 		Handler: mux,
// 	}

// 	go func() {
// 		log.Println("WebSocket bridge starting on localhost:3000")
// 		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
// 			log.Fatal("ListenAndServe: ", err)
// 		}
// 	}()

// 	stop := make(chan os.Signal, 1)
// 	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
// 	<-stop

// 	fmt.Println("shutting down...")
// 	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
// 	defer cancel()
// 	_ = srv.Shutdown(ctx)
// }

// func handleWebSocket(w http.ResponseWriter, r *http.Request) {
// 	// Upgrade HTTP connection to WebSocket
// 	ws, err := upgrader.Upgrade(w, r, nil)
// 	if err != nil {
// 		log.Println("Upgrade error:", err)
// 		return
// 	}
// 	defer ws.Close()

// 	// Create D-Bus connection for this client
// 	dbusConn, err := dbus.ConnectSystemBus()
// 	if err != nil {
// 		log.Println("Failed to connect to D-Bus:", err)
// 		return
// 	}
// 	defer dbusConn.Close()

// 	client := &Client{
// 		conn:     ws,
// 		send:     make(chan []byte, 256),
// 		dbusConn: dbusConn,
// 	}

// 	fmt.Println("client connected")

// 	// Start goroutines for reading and writing
// 	go client.transmitData()
// 	go client.receiveData()

// 	//initMsg := map[string]string{"activeUser": GetUsernameFromConnection(dbusConn)}

// 	//client.sendResponse(&initMsg)

// 	// Optional: subscribe to D-Bus signals and forward to client
// 	//go client.forwardSignals()
// 	fmt.Println("before done")

// 	<-r.Context().Done()

// 	fmt.Println("client disconnected")

// }

// func (c *Client) receiveData() {
// 	defer func() {
// 		c.conn.Close()
// 		close(c.send)
// 	}()

// 	for {
// 		_, rxdata, err := c.conn.ReadMessage()
// 		if err != nil {
// 			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
// 				log.Printf("WebSocket error: %v", err)
// 			}
// 			break
// 		}

// 		c.rxHandler(rxdata)

// 	}
// }

// func (c *Client) transmitData() {
// 	for txdata := range c.send {
// 		if err := c.conn.WriteMessage(websocket.TextMessage, txdata); err != nil {
// 			log.Printf("Write error: %v", err)
// 			return
// 		}
// 	}
// }

// func (c *Client) rxHandler(data []byte) {
// 	c.mu.Lock()
// 	defer c.mu.Unlock()

// 	msg := map[string]any{}

// 	if err := json.Unmarshal(data, &msg); err != nil {
// 		//c.sendError(msg.RequestID, fmt.Sprintf("Invalid JSON: %v", err))
// 		//continue
// 	}

// 	//fmt.Println("REQUEST: ", msg)

// 	if action, ok := msg["systemd"]; ok {

// 		service := msg["service"].(string)

// 		var systemdError error
// 		var status string = "success"

// 		switch action {
// 		case "stop":
// 			systemdError = _stopUnit(service)
// 		case "start":
// 			systemdError = _startUnit(service)
// 		case "restart":
// 			systemdError = _restartUnit(service)
// 		case "status":
// 			status, systemdError = _getUnitStatus(service)
// 		}

// 		if systemdError != nil {
// 			msg["systemd"] = "error"
// 			msg["service"] = service
// 			msg["error"] = systemdError.Error()
// 			c.sendResponse(&msg)
// 			return
// 		}

// 		msg["systemd"] = status
// 		msg["action"] = action
// 		msg["service"] = service
// 		msg["status"] = status

// 		c.sendResponse(&msg)
// 		return

// 	}

// 	if msg["status"] == "?" {
// 		msg["status"] = "up"
// 		c.sendResponse(&msg)
// 		return
// 	}

// 	if msg["activeUser"] == "?" {
// 		msg["activeUser"] = GetUsernameFromConnection(c.dbusConn)
// 		c.sendResponse(&msg)
// 		return
// 	}

// 	if _, ok := msg["dbusCall"]; ok {

// 		//fmt.Printf("msg: %s\n", msg)
// 		//fmt.Println("=====================================")
// 		var call DbusCall

// 		err := json.Unmarshal(data, &call)
// 		if err != nil {
// 			msg["dbusError"] = map[string]any{"error": err.Error()}
// 		}

// 		fmt.Println("args: ", call.Args)

// 		body, rsp, err := MakeDbusCall(c.dbusConn, call)
// 		if err != nil {

// 			msg["dbusError"] = map[string]any{"error": err.Error()}

// 			fmt.Println("ERROR WITH METHOD: ", call.Method)

// 			fmt.Println("ERROR FROM MAKE DBUS CALL: ", err.Error())

// 		}
// 		if len(call.Returns) > 0 {
// 			fmt.Println(call.Returns)
// 			fmt.Println("PARSING WITH RETURNS??????????????")
// 			rsp = ParseWithReturnType(call.Returns, body)
// 		}

// 		msg["dbusResponse"] = rsp

// 		c.sendResponse(&msg)
// 		return
// 	}

// }

// func (c *Client) sendResponse(resp *map[string]any) {

// 	for k, v := range *resp {
// 		log.Printf("%s: %T %#v", k, v, v)
// 	}

// 	txdata, err := json.Marshal(resp)
// 	if err != nil {
// 		log.Printf("Marshal error: %v", err)
// 		return
// 	}
// 	c.send <- txdata
// }

// Forward D-Bus signals to WebSocket client
//func (c *Client) forwardSignals() {
//	// Add signal match rules as needed
//	c.dbusConn.BusObject().Call("org.freedesktop.DBus.AddMatch", 0,
//		"type='signal',interface='org.freedesktop.DBus.Properties',member='PropertiesChanged'")
//
//	signals := make(chan *dbus.Signal, 10)
//	c.dbusConn.Signal(signals)
//
//	for signal := range signals {
//		signalMsg := map[string]interface{}{
//			"type":      "signal",
//			"path":      string(signal.Path),
//			"interface": signal.Name,
//			"body":      signal.Body,
//		}
//
//		data, err := json.Marshal(signalMsg)
//		if err != nil {
//			log.Printf("Signal marshal error: %v", err)
//			continue
//		}
//
//		select {
//		case c.send <- data:
//		default:
//			// Channel full, skip this signal
//		}
//	}
//}

func StartBridgeProxy(targetUser string) error {
	dbusPath := "/var/run/dbus/system_bus_socket"

	listener, err := net.Listen("tcp", "localhost:3000")
	if err != nil {
		return err
	}

	fmt.Println("accepting connections")

	go func() {
		for {
			clientConn, err := listener.Accept()
			if err != nil {
				return
			}
			go proxyConn(clientConn, dbusPath)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop

	fmt.Println("shutting down...")
	listener.Close() // closing the listener is sufficient - Accept() will error and the goroutine exits
	return nil
}

func proxyConn(client net.Conn, dbusSocketPath string) {
	defer client.Close()

	dbusSocket, err := net.Dial("unix", dbusSocketPath)
	if err != nil {
		log.Println(err)
		return
	}
	defer dbusSocket.Close()

	// Auth on the Unix socket using our real creds
	uid := os.Getuid()
	hexUID := hex.EncodeToString([]byte(strconv.Itoa(uid)))

	dbusSocket.Write([]byte("\x00"))
	fmt.Fprintf(dbusSocket, "AUTH EXTERNAL %s\r\n", hexUID)
	okLine := readLine(dbusSocket) // "OK <guid>\r\n"
	fmt.Fprintf(dbusSocket, "BEGIN\r\n")

	// Consume client's auth sequence and replace with our OK
	client.Read(make([]byte, 1)) // null byte
	readLine(client)             // AUTH EXTERNAL ...
	client.Write([]byte(okLine)) // send real OK back
	readLine(client)             // BEGIN

	// Now both sides are auth'd - pure pipe
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
