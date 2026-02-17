#!/usr/bin/env bash
uv run nicegui-pack --onefile \
                    --name "ns2-ui" \
                    --add-data "ns2_ui/assets:ns2/assets" \
                    --add-data "ns2_ui/introspection:ns2/introspection" ns2_ui/main.py

