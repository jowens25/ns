
#=================================================================================================================
#SETUP INFO / PROCESS
#=================================================================================================================

sudo systemctl disable variscite-bt.service
sudo systemctl disable variscite-wifi.service
echo "Disabled variscite bt and wifi services..."

sudo apt update
sudo apt install network-manager
sudo systemctl disable NetworkManager-wait-online.service
sudo apt install nginx
sudo apt install firewalld
sudo apt install snmpd
sudo apt install socat
echo "Installed main dependencies..."

curl https://jowens25.gitlab.io/novus/install.sh | sh

sudo apt install ns-serial-mux
sudo apt install ns-agent
sudo apt install ns-admin

sudo ns reset
#sudo reboot now
#ns account add admin admin -a
