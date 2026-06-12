ns-admin test plan


1. Login

    Navigate to https://<your-ip>
    (the ip can be found on the front panel)

    Note that in the support tab you can reset the default user if you lock yourself out.

    Login with username: novus password: novus123 - very secure

    You should land on the Status page

2. Status

    The status page is parsing the strings that come from the 4078. Check them out. Look for weird things.

    In the top right you can change the time zone of the system

    In the bottom left you can see the version of the control panel

    (run ns version and make sure the versions match)

    In the top left you can toggle the menu by pressing the 3 horizontal bars.

3. System

    The system page shows services and logs.

    You can search for and select the services you'd like to get the logs of.

    You can select the time and type of logs youd like to get. 

    Select some services, fetch logs, and try to download and view

    (may limit the services in view to only the ones we care about)

4. Network

    The network page has the firewalld and networking panels.

    In the firewall panel you can toggle if the firewall is active or not.

    One way to test this is to remove ssh from the allowed services. Disable the firewalld and attempt to ssh in.

    Then reenable the firewalld and attempt to ssh in. If the firewall is working you should be blocked because that service was removed.

    You can add services, remove services. You can make a new zone. This is a little funny because we only have 1 interface. If you have a wifi and ethernet interface it can make more sense to define a more secure zone for your wifi and less secure zone for your ethernet since you may have thought about what you are plugging into. 

    Regardless you can delete and add zones. 

    In the networking page the main thing you can do is change the ip and add other DNS or routes or change the ip method. 

    Most people will want to set a static Ip. This means selecting the interface in the table and editing the ipv4 section and setting the method to manual and configuring your desired ip. Try that. Then set it back to auto. You will lose connection to the app and will need to renavigate to https://<your-new-ip>

5. SNMP

    The snmp page allows you to download the mib, reset the config and disable the service if you like. 

    Start by downloading the mib (and downloading some kind of mib broswer for running these tests. ManageEngine has a good one for free.)

    The default config include a v2c community of novus so you can start with getting, setting, walking snmp tree with that. 

    It takes some configuration of the mib browser for things to work right. Just add your user into its settings.

    After that make some snmp calls.

    Then expand into adding traps, v3 users, v3 traps. Its require that a v3 trap have the same engineID and username as a v3 user configured on the system. So copy and paste those in when making it... (may need to add a warning or note for that.)

6. Accounts

    The accounts page allows your to add, remove, edit user passwords. 

    Admins should be able to change their own password or the password of a non-admin.
    Users should not be able to change any password but their own. 
    The "remote login" is not valid
    The password policy should be only configurable by an admin.
    
    Add an admin and a user and then log into the app and through another interface using those users. For example ssh to both.

7. Terminal

    The terminal page allows users to run commands. Its not a fully functional terminal but it does allow some basic commands to work. Try running some commands. 

    