#!/usr/bin/env python3
"""Test Polkit authorization check."""

import asyncio
import os
from pathlib import Path
from dbus_next import Message, Variant
from dbus_next.aio import MessageBus

from ns2.api.dbus import get_dbus


def get_process_start_time(pid: int) -> int:
    """Get process start time in microseconds since boot (for PolicyKit)."""
    stat = Path(f"/proc/{pid}/stat").read_text()
    parts = stat.split()
    paren_end = stat.index(")")
    after_paren = stat[paren_end + 1 :].split()
    starttime_ticks = int(after_paren[19])

    CLOCK_TICKS = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
    starttime_us = int((starttime_ticks / CLOCK_TICKS) * 1_000_000)
    return starttime_us


async def check_authorization(action_id: str) -> dict:
    """Check if the calling process is authorized for action."""
    bus = await get_dbus()

    # Get current process info
    pid = os.getpid()
    uid = os.getuid()
    start_time = get_process_start_time(pid)

    import pwd

    username = pwd.getpwuid(uid).pw_name

    print(f"Checking authorization for:")
    print(f"  PID: {pid}")
    print(f"  UID: {uid}")
    print(f"  Username: {username}")
    print(f"  Start time: {start_time}")
    print(f"  Action: {action_id}")
    print(f"  Bus unique name: {bus.unique_name}")

    # Subject is the process requesting authorization
    # Using system-bus-name is correct for D-Bus clients
    subject = [
        "system-bus-name",
        {"name": Variant("s", bus.unique_name)},
    ]

    details = {}
    flags = 1  # No user interaction
    cancellation_id = ""

    try:
        result = await bus.call(
            Message(
                destination="org.freedesktop.PolicyKit1",
                path="/org/freedesktop/PolicyKit1/Authority",
                interface="org.freedesktop.PolicyKit1.Authority",
                member="CheckAuthorization",
                signature="(sa{sv})sa{ss}us",
                body=[
                    subject,
                    action_id,
                    details,
                    flags,
                    cancellation_id,
                ],
            )
        )

        # Result is a struct: (is_authorized, is_challenge, details)
        auth_result = result.body[0]

        print(f"Authorization Result:")
        print(f"  Is Authorized: {auth_result[0]}")
        print(f"  Is Challenge: {auth_result[1]}")
        print(f"  Details: {auth_result[2]}")

        return {
            "is_authorized": auth_result[0],
            "is_challenge": auth_result[1],
            "details": auth_result[2],
        }

    except Exception as e:
        print(f"Error checking authorization: {e}")
        raise
    # finally:
    # bus.disconnect()


async def main():
    """Run authorization tests."""
    action_id = "com.novus.ns.snmp.reset"

    print("=" * 60)
    print("Testing Polkit Authorization")
    print("=" * 60)
    print()

    result = await check_authorization(action_id)

    print()
    print("=" * 60)
    if result["is_authorized"]:
        print("✓ AUTHORIZED")
    else:
        print("✗ NOT AUTHORIZED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
