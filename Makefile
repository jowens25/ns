#!/usr/bin/make -f

.DEFAULT_GOAL := build

PYINSTALLER = uv run pyinstaller
NICEGUI_PACK = uv run nicegui-pack

# Define output targets
DBUS_TARGET = dist/ns-dbus
UI_TARGET = dist/ns-ui

PREFIX ?= /usr
DESTDIR ?=

build-dbus:
	$(PYINSTALLER) --onefile --name ns-dbus ns2/dbus.py

build-ui:
	$(NICEGUI_PACK) --onefile --name ns-ui \
		--add-data "ns2/assets:ns2/assets" \
		--add-data "ns2/introspection:ns2/introspection" \
		ns2/main.py

build: build-dbus build-ui

.PHONY: build-dbus build-ui build

install: build
	install -D -m 755 $(DBUS_TARGET) $(DESTDIR)$(PREFIX)/bin/ns-dbus
	install -D -m 755 $(UI_TARGET) $(DESTDIR)$(PREFIX)/bin/ns-ui
	install -D -m 755 configs/com.novus.ns.conf $(DESTDIR)$(PREFIX)/share/dbus-1/system.d/com.novus.ns.conf 
	install -D -m 755 configs/ns2.xml $(DESTDIR)$(PREFIX)/lib/firewalld/services/ns2.xml
clean:
	rm -rf build dist *.spec
	rm -f *.pyc
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: clean install