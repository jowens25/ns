#!/usr/bin/env bash
uv run pyinstaller --onefile \
                    --name "ns2-dbus" \
                    ns2_service/main.py

