rm ns
go build .
echo "TEST.sh: built"
sudo cp ns /usr/bin/ns
echo "TEST.sh: copied for global use"


sudo cp ~/Projects/ns-admin/configs/com.novus.ns.conf /usr/share/dbus-1/system.d/com.novus.ns.conf
sudo cp ~/Projects/ns-admin/configs/com.novus.ns.policy /usr/share/polkit-1/actions/com.novus.ns.policy
echo "TEST.sh: copied policy and ns.conf"

echo "TEST.sh: Starting dbus server..."
sudo ns dbus export

