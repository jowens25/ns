go build .
echo "TEST.sh: built"
sudo cp ns /usr/bin/ns
echo "TEST.sh: copied for global use"

echo "TEST.sh: Starting dbus server..."
sudo ns dbus export -d