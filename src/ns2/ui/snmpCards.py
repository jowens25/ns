from nicegui import ui
from ns2.lib.snmp import V3Trap, V3User, V2Trap, V2User

portValidation = {
    "Port must be a number": lambda value: value.isdigit(),
}

sourceValidation = {
    "Please enter a valid ip address, network or default": lambda value: len(value) > 0
}

communityValidation = {"Please enter a valid community": lambda value: len(value) > 0}

hostValidation = {"Please enter a valid host": lambda value: len(value) > 0}


usernameValidation = {
    "Username must be at least 5 characters": lambda value: len(value) >= 5,
    "Username must be 24 or less characaters": lambda value: 24 >= len(value),
}


passphraseValidation = {
    "Passphrase must be at least 8 characters": lambda value: len(value) >= 8,
    "Passphrase must be 24 or less characaters": lambda value: 24 >= len(value),
}

engineValidation = {"Please enter a valid engine id": lambda value: len(value) > 0}


async def v2UserCardBody(user: V2User) -> list:
    version = (
        ui.select(label="Version", options=["v2c", "v1"])
        .classes("w-full")
        .props("dense")
        .bind_value(user, "Version")
    )
    permissions = (
        ui.select(label="Permissions", options=["rwnoauthgroup", "ronoauthgroup"])
        .classes("w-full")
        .props("dense")
        .bind_value(user, "Permissions")
    )
    community = (
        ui.input(
            "Community",
            validation=communityValidation,
        )
        .classes("w-full")
        .props("dense")
        .bind_value(user, "Community")
    )
    source = (
        ui.input("Source / IP Address", validation=sourceValidation)
        .classes("w-full")
        .props("dense")
        .bind_value(user, "Source")
    )

    return [version, permissions, community, source]


async def v2TrapCardBody(trap: V2Trap) -> list:

    version = (
        ui.select(["1", "2c"], label="Version", value="2c")
        .bind_value(trap, "Version")
        .classes("w-full")
        .props("dense")
    )

    community = (
        ui.input("Community", validation=communityValidation)
        .bind_value(trap, "Community")
        .classes("w-full")
        .props("dense")
    )

    protocol = (
        ui.select(["udp", "tcp", "upd6", "tcp6"], label="Protocol")
        .bind_value(trap, "Protocol")
        .classes("w-full")
        .props("dense")
    )
    host = ui.input("Host").bind_value(trap, "Host").classes("w-full").props("dense")
    port = (
        ui.input("Port", validation=portValidation)
        .bind_value(trap, "Port")
        .classes("w-full")
        .props("dense")
    )

    return [version, community, protocol, host, port]


async def v3UserCardBody(user: V3User) -> list:
    version = (
        ui.input(label="Version")
        .classes("w-full")
        .props("dense")
        .bind_value(user, "Version")
    )
    version.disable()
    username = (
        ui.input(label="Username", validation=usernameValidation)
        .classes("w-full")
        .props("dense")
        .bind_value(user, "Username")
    ).props("debounce=1000")
    permissions = (
        ui.select(label="Permissions", options=["roprivgroup", "rwprivgroup"])
        .classes("w-full")
        .props("dense")
        .bind_value(user, "Permissions")
    )
    auth_type = (
        ui.select(label="Auth Alg", options=["SHA", "MD5"])
        .classes("w-full")
        .props("dense")
        .bind_value(user, "AuthType")
    )
    auth_pass = (
        ui.input(label="Auth Passphrase", validation=passphraseValidation)
        .classes("w-full")
        .props("dense")
        .bind_value(user, "AuthPassphrase")
    ).props("debounce=1000")
    priv_type = (
        ui.select(label="Priv Alg", options=["AES", "DES"])
        .classes("w-full")
        .props("dense")
        .bind_value(user, "PrivType")
    )
    priv_pass = (
        ui.input(label="Auth Passphrase", validation=passphraseValidation)
        .classes("w-full")
        .props("dense")
        .bind_value(user, "PrivPassphrase")
    ).props("debounce=1000")

    return [version, username, permissions, auth_type, auth_pass, priv_type, priv_pass]


async def v3TrapCardBody(trap: V3Trap) -> list:

    engineid = (
        ui.input("Engine ID", validation=engineValidation)
        .bind_value(trap, "EngineId")
        .classes("w-full")
        .props("dense")
    )
    username = (
        ui.input("Username", validation=usernameValidation)
        .bind_value(trap, "Username")
        .classes("w-full")
        .props("dense")
    )

    authType = (
        ui.select(["MD5", "SHA"], label="Authentication Type", value="MD5")
        .bind_value(trap, "AuthType")
        .classes("w-full")
        .props("dense")
    )

    privType = (
        ui.select(["DES", "AES"], label="Privacy Type", value="DES")
        .bind_value(trap, "PrivType")
        .classes("w-full")
        .props("dense")
    )

    protocol = (
        ui.select(["udp", "tcp", "upd6", "tcp6"], label="Protocol")
        .bind_value(trap, "Protocol")
        .classes("w-full")
        .props("dense")
    )

    host = (
        ui.input("Host", validation=hostValidation)
        .bind_value(trap, "Host")
        .classes("w-full")
    )

    port = (
        ui.input("Port", validation=portValidation)
        .bind_value(trap, "Port")
        .classes("w-full")
        .props("dense")
    )

    return [engineid, username, authType, privType, protocol, host, port]
