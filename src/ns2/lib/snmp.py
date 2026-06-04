from dataclasses import dataclass
from typing import Optional
from nicegui import ui

snmp_config_file = "/etc/snmp/snmpd.conf.d/novus-snmpd.conf"
default_persistent_dir_path = "/var/lib/snmp"


USM_OID_MAP = {
    # Authentication Protocols (RFC 3414)
    "1.3.6.1.6.3.10.1.1.1": "NoAuth",
    ".1.3.6.1.6.3.10.1.1.2": "MD5",
    ".1.3.6.1.6.3.10.1.1.3": "SHA",
    "1.3.6.1.6.3.10.1.1.4": "HMAC-SHA2-224",
    "1.3.6.1.6.3.10.1.1.5": "HMAC-SHA2-256",
    # Privacy Protocols (RFC 3414 + 3826)
    "1.3.6.1.6.3.10.1.2.1": "NoPriv",
    ".1.3.6.1.6.3.10.1.2.2": "DES",
    ".1.3.6.1.6.3.10.1.2.4": "AES",
    "1.3.6.1.6.3.10.1.2.5": "AES-192",
    "1.3.6.1.6.3.10.1.2.6": "AES-256",
}


@dataclass
class Group:
    Permissions: Optional[str] = None
    Version: Optional[str] = None
    SecName: Optional[str] = None


# trapsess -v 2c -c novus udp:10.1.10.205:162
# trapsess -v 3 -u JACOBOWENS -l authPriv -a SHA -A JACOBOWENS -x AES -X JACOBOWENS udp:10.1.10.205:162


@dataclass
class V2Trap:
    Version: Optional[str] = "2c"
    Community: Optional[str] = ""
    Protocol: Optional[str] = "udp"
    Host: Optional[str] = ""
    Port: Optional[str] = "162"

    def from_dict(trapDict: dict):
        user = V2User(
            Version=trapDict.get("Version"),
            Community=trapDict.get("Community"),
            Protocol=trapDict.get("Protocol"),
            Host=trapDict.get("Host"),
            Port=trapDict.get("Port"),
        )
        return user


@dataclass
class V3Trap:
    Version: Optional[str] = "3"
    Username: Optional[str] = ""
    EngineId: Optional[str] = ""
    AuthType: Optional[str] = "SHA"
    PrivType: Optional[str] = "AES"
    Protocol: Optional[str] = "udp"
    Host: Optional[str] = ""
    Port: Optional[str] = "162"

    def from_dict(trapDict: dict):
        return V3Trap(
            Version=trapDict.get("Version"),
            Username=trapDict.get("Username"),
            EngineId=trapDict.get("EngineId"),
            AuthType=trapDict.get("AuthType"),
            PrivType=trapDict.get("PrivType"),
            Protocol=trapDict.get("Protocol"),
            Host=trapDict.get("Host"),
            Port=trapDict.get("Port"),
        )


@dataclass
class V3User:
    Username: Optional[str] = ""
    Version: Optional[str] = "usm"
    EngineId: Optional[str] = ""
    AuthType: Optional[str] = "SHA"
    AuthPassphrase: Optional[str] = ""
    PrivType: Optional[str] = "AES"
    PrivPassphrase: Optional[str] = ""
    Permissions: Optional[str] = "rwprivgroup"

    def from_dict(userDict: dict):
        user = V3User(
            UserName=userDict.get("Username"),
            Version=userDict.get("Version"),
            EngineId=userDict.get("EngineId"),
            AuthType=userDict.get("AuthType"),
            AuthPassphrase=userDict.get("AuthPassphrase"),
            PrivType=userDict.get("PrivType"),
            PrivPassphrase=userDict.get("PrivPassphrase"),
            Permissions=userDict.get("Permissions"),
        )
        return user


@dataclass
class V2User:
    Community: str = ""
    Version: str = "v2c"
    Permissions: str = "rwnoauthgroup"
    Source: str = "default"
    SecurityName: str = ""

    def from_dict(userDict: dict):
        user = V2User(
            Community=userDict.get("Community"),
            Version=userDict.get("Version"),
            Permissions=userDict.get("Permissions"),
            Source=userDict.get("Source"),
            SecurityName=userDict.get("SecurityName"),
        )
        return user


def are_you_sure_you_want_to(action_message: str) -> bool:
    with ui.dialog() as dialog, ui.card().props("flat"):
        ui.label(f"Are you sure you want to {action_message}?")

        with ui.row():
            ui.button("Yes", on_click=lambda: dialog.submit(True)).props("flat")
            ui.button("No", on_click=lambda: dialog.submit(False)).props("flat")
    return dialog
