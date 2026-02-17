#!/usr/bin/env bash
uv run nicegui-pack --onefile \
                    --name "ns2bin" \
                    --add-data "ns2/assets:ns2/assets" \
                    --add-data "ns2/introspection:ns2/introspection" ns2/main.py

