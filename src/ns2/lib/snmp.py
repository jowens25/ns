from dataclasses import dataclass
from typing import Optional

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
    Community: Optional[str] = ""
    DestIpVersion: Optional[str] = ""
    DestIp: Optional[str] = ""
    Port: Optional[int] = 162


@dataclass
class V3Trap:
    User: Optional[str] = ""
    DestIpVersion: Optional[str] = ""
    DestIp: Optional[str] = ""
    Port: Optional[int] = 162
    EngineId: Optional[str] = ""
    AuthType: Optional[str] = ""
    AuthPass: Optional[str] = ""
    PrivType: Optional[str] = ""
    PrivPass: Optional[str] = ""


@dataclass
class V3User:
    Username: Optional[str] = ""
    Version: Optional[str] = "usm"
    AuthType: Optional[str] = "SHA"
    AuthPassphrase: Optional[str] = ""
    PrivType: Optional[str] = "AES"
    PrivPassphrase: Optional[str] = ""
    Permissions: Optional[str] = "rwprivgroup"

    def from_dict(userDict: dict):
        user = V3User(
            UserName=userDict.get("Username"),
            Version=userDict.get("Version"),
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
    Source: str = ""
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
