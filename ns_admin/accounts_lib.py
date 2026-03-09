import subprocess


def addGroup(groupName, GID):
    try:
        subprocess.run(
            ["sudo", "groupadd", groupName, "-g", GID],
            check=True,
            capture_output=True,
            text=True,
        )
        return "added group"
    except subprocess.CalledProcessError as e:
        return e.stderr


def removeGroup(groupName):
    try:
        subprocess.run(
            ["sudo", "groupdel", groupName], check=True, capture_output=True, text=True
        )

        return "removed group"
    except subprocess.CalledProcessError as e:
        return e.stderr


def addUserToGroup(username, groupname):
    return subprocess.run(
        ["gpasswd", "-a", username, groupname],
        check=True,
        capture_output=True,
        text=True,
    )


def removeUserFromGroup(username, groupname):
    return subprocess.run(
        ["gpasswd", "-d", username, groupname],
        check=True,
        capture_output=True,
        text=True,
    )
