package lib

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"os/user"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/godbus/dbus/v5"
	"github.com/gorilla/websocket"
)

type DbusCall struct {
	Destination string          `json:"Destination" binding:"required"` // object
	Path        dbus.ObjectPath `json:"Path" binding:"required"`        // object
	Method      string          `json:"Method" binding:"required"`      // call
	Args        []any           `json:"Args"`                           // call
	Signature   string          `json:"Signature" binding:"required"`
}

func MakeDbusCall(conn *dbus.Conn, call DbusCall) (any, error) {

	var result any

	err := MyCall(conn, call.Destination, call.Path, call.Method, 0, call.Signature, call.Args...).Store(&result)
	if err != nil {
		return nil, err
	}
	return result, nil

}

func MyCall(conn *dbus.Conn, destination string, path dbus.ObjectPath, method string, flags dbus.Flags, signature string, args ...any) *dbus.Call {

	iface := ""
	i := strings.LastIndex(method, ".")
	if i != -1 {
		iface = method[:i]
	}
	method = method[i+1:]

	msg := new(dbus.Message)
	msg.Type = dbus.TypeMethodCall
	msg.Flags = flags & (dbus.FlagNoAutoStart | dbus.FlagNoReplyExpected)
	msg.Headers = make(map[dbus.HeaderField]dbus.Variant)
	msg.Headers[dbus.FieldPath] = dbus.MakeVariant(path)
	msg.Headers[dbus.FieldDestination] = dbus.MakeVariant(destination)
	msg.Headers[dbus.FieldMember] = dbus.MakeVariant(method)

	if iface != "" {
		msg.Headers[dbus.FieldInterface] = dbus.MakeVariant(iface)
	}

	msg.Body = args

	if signature != "" {
		sig, err := dbus.ParseSignature(signature)
		if err != nil {
			panic(err)
		}
		msg.Headers[dbus.FieldSignature] = dbus.MakeVariant(sig)
	}

	fmt.Println("Message headers:", msg.Headers)

	ch := make(chan *dbus.Call, 1)
	conn.SendWithContext(context.Background(), msg, ch)
	return <-ch
}

// calls connect call with default:
// com.novus.ns
// /com/novus/ns
func CallNovusService(subinterfaceMethod string, args []any) any {

	return ConnectCall("com.novus.ns", "/com/novus/ns", "com.novus.ns."+subinterfaceMethod, args)

}

func ConnectCall(destination string, path string, method string, args []any) any {

	//	conn, err := dbus.ConnectSystemBus()
	//
	//	if err != nil {
	//		fmt.Fprintln(os.Stderr, "Failed to connect to sys bus:", err)
	//		os.Exit(1)
	//	}
	//	defer conn.Close()
	//	r, err := MakeDbusCall(conn, DbusCall{Destination: destination, Path: path, Method: method, Args: args})
	//
	//	if err != nil {
	//		return err
	//	}
	//	return r

	var j any = 1

	return j

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
		res, err := MakeDbusCall(conn, call)
		if err != nil {
			c.JSON(http.StatusOK, map[string]string{"Dbus": err.Error()})
			return
		}

		//log.Println(res)
		c.JSON(http.StatusOK, res)
		return

	}
}

// run from cmd
func OpenDbusConnection() string {
	// opens dbus connection as user
	conn, err := dbus.ConnectSystemBus()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Failed to connect to sys bus:", err)
		os.Exit(1)
	}
	return conn.Names()[0]
}

func InitHttpBridge() {

	// opens dbus connection as user
	conn, err := dbus.ConnectSystemBus()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Failed to connect to sys bus:", err)
		os.Exit(1)
	}
	defer conn.Close()

	fmt.Println(conn.Names()[0])

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

func InitWebSocketBridge() {
	mux := http.NewServeMux()
	mux.HandleFunc("/bridge", handleWebSocket)

	srv := &http.Server{
		Addr:    "localhost:3000",
		Handler: mux,
	}

	go func() {
		log.Println("WebSocket bridge starting on localhost:3000")
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal("ListenAndServe: ", err)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop

	fmt.Println("shutting down...")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	_ = srv.Shutdown(ctx)
}

func handleWebSocket(w http.ResponseWriter, r *http.Request) {
	// Upgrade HTTP connection to WebSocket
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("Upgrade error:", err)
		return
	}
	defer ws.Close()

	// Create D-Bus connection for this client
	dbusConn, err := dbus.ConnectSystemBus()
	if err != nil {
		log.Println("Failed to connect to D-Bus:", err)
		return
	}
	defer dbusConn.Close()

	client := &Client{
		conn:     ws,
		send:     make(chan []byte, 256),
		dbusConn: dbusConn,
	}

	fmt.Println("client connected")

	// Start goroutines for reading and writing
	go client.transmitData()
	go client.receiveData()

	//initMsg := map[string]string{"activeUser": GetUsernameFromConnection(dbusConn)}

	//client.sendResponse(&initMsg)

	// Optional: subscribe to D-Bus signals and forward to client
	//go client.forwardSignals()
	fmt.Println("before done")

	<-r.Context().Done()

	fmt.Println("client disconnected")

}

func (c *Client) receiveData() {
	defer func() {
		c.conn.Close()
		close(c.send)
	}()

	for {
		_, rxdata, err := c.conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("WebSocket error: %v", err)
			}
			break
		}

		c.rxHandler(rxdata)

	}
}

func (c *Client) transmitData() {
	for txdata := range c.send {
		if err := c.conn.WriteMessage(websocket.TextMessage, txdata); err != nil {
			log.Printf("Write error: %v", err)
			return
		}
	}
}

func (c *Client) rxHandler(data []byte) {
	c.mu.Lock()
	defer c.mu.Unlock()

	msg := map[string]any{}

	if err := json.Unmarshal(data, &msg); err != nil {
		//c.sendError(msg.RequestID, fmt.Sprintf("Invalid JSON: %v", err))
		//continue
	}

	if msg["status"] == "?" {
		msg["status"] = "up"
		c.sendResponse(&msg)
		return
	}

	if msg["activeUser"] == "?" {
		msg["activeUser"] = GetUsernameFromConnection(c.dbusConn)
		c.sendResponse(&msg)
		return
	}

	_, ok := msg["dbusCall"]
	if ok {

		//fmt.Printf("msg: %s\n", msg)
		//fmt.Println("=====================================")
		var call DbusCall

		err := json.Unmarshal(data, &call)
		if err != nil {
			msg["dbusError"] = map[string]any{"error": err.Error()}
		}
		//call.Destination = msg["destination"].(string)
		//call.Path = msg["path"].(string)
		//call.Method = msg["method"].(string)
		//
		//tempArgs := msg["args"].([]any)
		//tempSigs := msg["signature"].([]any)
		//finalArgs := []any{}
		//
		//for i := range tempArgs {
		//
		//	sig, _ := dbus.ParseSignature(tempSigs[i].(string))
		//
		//	v, _ := dbus.ParseVariant(tempArgs[i].(string), sig)
		//
		//	finalArgs = append(finalArgs, v.Value())
		//}
		//
		//call.Args = finalArgs
		//fmt.Println("final args")
		//fmt.Println(call.Args)
		//fmt.Println("=====================================")

		rsp, err := MakeDbusCall(c.dbusConn, call)
		if err != nil {

			msg["dbusError"] = map[string]any{"error": err.Error()}

			fmt.Printf("error after makedbus call: %s\n", err.Error())

		}
		fmt.Println(rsp)

		msg["dbusResponse"] = rsp
		c.sendResponse(&msg)
		return
	}

	fmt.Printf("%s\n", msg)

	// Parse incoming message
	//var msg DbusMessage
	//if err := json.Unmarshal(message, &msg); err != nil {
	//	c.sendError(msg.RequestID, fmt.Sprintf("Invalid JSON: %v", err))
	//	continue
	//}

	//var response DbusResponse
	//response.RequestID = msg.RequestID

	fmt.Println(msg)

	//switch msg.Type {
	//case "call":
	//	obj := c.dbusConn.Object(msg.Destination, dbus.ObjectPath(msg.Path))
	//	call := obj.Call(msg.Interface+"."+msg.Member, 0, msg.Args...)
	//
	//	if call.Err != nil {
	//		response.Success = false
	//		response.Error = call.Err.Error()
	//	} else {
	//		response.Success = true
	//		response.Result = call.Body
	//	}
	//
	//case "get":
	//	obj := c.dbusConn.Object(msg.Destination, dbus.ObjectPath(msg.Path))
	//	variant, err := obj.GetProperty(msg.Interface + "." + msg.Member)
	//
	//	if err != nil {
	//		response.Success = false
	//		response.Error = err.Error()
	//	} else {
	//		response.Success = true
	//		response.Result = []interface{}{variant.Value()}
	//	}
	//
	//case "set":
	//	obj := c.dbusConn.Object(msg.Destination, dbus.ObjectPath(msg.Path))
	//	err := obj.SetProperty(msg.Interface+"."+msg.Member, dbus.MakeVariant(msg.Args[0]))
	//
	//	if err != nil {
	//		response.Success = false
	//		response.Error = err.Error()
	//	} else {
	//		response.Success = true
	//	}
	//
	//case "test":
	//	c.send <- []byte("hello world")
	//
	//default:
	//	response.Success = false
	//	response.Error = "Unknown message type"
	//}

	// Send response back to client
	//c.sendResponse(&response)
}

func (c *Client) sendResponse(resp *map[string]any) {
	txdata, err := json.Marshal(resp)
	if err != nil {
		log.Printf("Marshal error: %v", err)
		return
	}
	c.send <- txdata
}

//func (c *Client) sendError(requestID, errMsg string) {
//	resp := &DbusResponse{
//		RequestID: requestID,
//		Success:   false,
//		Error:     errMsg,
//	}
//	c.sendResponse(resp)
//}

// Forward D-Bus signals to WebSocket client
func (c *Client) forwardSignals() {
	// Add signal match rules as needed
	c.dbusConn.BusObject().Call("org.freedesktop.DBus.AddMatch", 0,
		"type='signal',interface='org.freedesktop.DBus.Properties',member='PropertiesChanged'")

	signals := make(chan *dbus.Signal, 10)
	c.dbusConn.Signal(signals)

	for signal := range signals {
		signalMsg := map[string]interface{}{
			"type":      "signal",
			"path":      string(signal.Path),
			"interface": signal.Name,
			"body":      signal.Body,
		}

		data, err := json.Marshal(signalMsg)
		if err != nil {
			log.Printf("Signal marshal error: %v", err)
			continue
		}

		select {
		case c.send <- data:
		default:
			// Channel full, skip this signal
		}
	}
}
