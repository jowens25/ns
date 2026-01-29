cp ns.service /etc/systemd/system/ns.service

systemctl daemon-reload

systemctl restart ns.service

systemctl status ns.service