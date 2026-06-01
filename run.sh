cd ./src/ns2/backend/ns/

go build .

sudo cp ns /usr/bin/ns

cd ..
cd .. 
cd ..
cd ..

sudo cp configs/com.novus.ns.conf /usr/share/dbus-1/system.d/com.novus.ns.conf

sudo ns dbus export &

# start ui
uv run ./src/ns2/ui/main.py

sudo rm /usr/share/dbus-1/system.d/com.novus.ns.conf
echo "REMOVED DBUS CONFIG"

sudo rm /usr/bin/ns
echo "REMOVE NS BIN"

echo "FINISHED"