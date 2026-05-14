import requests


def bridgeCall(destination, path, method, args=None):
    try:
        resp = requests.post(
            "http://localhost:8080/call",
            json={
                "Destination": destination,
                "Path": path,
                "Method": method,
                "Args": args or [],
            },
        )
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as e:
        print("http exception: ", e)

    finally:
        return resp.json()


def PamAuthenticate(username, password) -> bool:

    res = bridgeCall(
        "com.novus.ns",
        "/com/novus/ns",
        "com.novus.ns.pam.Authenticate",
        [username, password],
    )

    return res
