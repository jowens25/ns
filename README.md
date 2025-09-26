# ns

Old Debian build to new Debian build

1. install old deb
2. boot old
3. edit /etc/network/interfaces to connect to network
4. reboot
5. scp deb to variscite
6. attempt to install deb
7. First error "trying to overwrite /etc/login.defs"
8. fixed with --force-overwrite
9. attempt tp install deb again.
10. new errors: dpkg depends on nginx, pure-ftpd, xinetd and those are not installed
11. install nginx, pure-ftpd, xinetd
12. realized packages might be out of date so.
13. sudo apt update, sudo apt upgrade
14. Cert is not trusted because the date is off.
15. Fixed with sudo date -s "$(wget --method=HEAD -qSO- --max-redirect=0 google.com 2>&1 | sed -n 's/^ *Date: *//p')"
16. run apt update and upgrade gain
17. errors were "broken install"
18. Ran suggested apt --fix-broken install
19. ran update and upgrade again.
20. Errrors from broken nginx isntall
21. had to run dpkg -r ns to remove ns and then install ngnix and stuff
22. okay, found that on init was unable to open database file
23. also unable to create bash completeation scripts