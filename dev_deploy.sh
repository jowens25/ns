#!/bin/bash

trap 'kill -- -$$' EXIT SIGINT SIGTERM

#./../ns-socket/ns-socket-server /dev/ttyUSB0 &

./.venv/bin/python ns_dbus_service.py &

./.venv/bin/python main.py 8080 &

ngrok http 8080 &

echo WAITING...

wait