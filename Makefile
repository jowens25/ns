#!/usr/bin/make -f

.DEFAULT_GOAL := build

NICEGUI_PACK = uv run nicegui-pack

# Define output target
APP_TARGET = dist/ns2

PREFIX ?= /usr
DESTDIR ?=

build:
	$(NICEGUI_PACK) --onedir --name ns2 \
		--add-data "ns2/assets:ns2/assets" \
		--add-data "ns2/introspection:ns2/introspection" \
		ns2/main.py

.PHONY: build

install: build
	# Install the entire onedir build to /usr/lib/ns2
	install -d $(DESTDIR)$(PREFIX)/lib/ns2
	cp -r dist/ns2/* $(DESTDIR)$(PREFIX)/lib/ns2/
	
	# Symlink the executable to /usr/bin
	install -d $(DESTDIR)$(PREFIX)/bin
	ln -sf $(PREFIX)/lib/ns2/ns2 $(DESTDIR)$(PREFIX)/bin/ns2
	
	# Install config files
	install -D -m 644 configs/com.novus.ns.conf $(DESTDIR)$(PREFIX)/share/dbus-1/system.d/com.novus.ns.conf 
	install -D -m 644 configs/ns2.xml $(DESTDIR)$(PREFIX)/lib/firewalld/services/ns2.xml
	install -D -m 644 configs/ns2-ui.conf $(DESTDIR)/etc/nginx/sites-available/ns2-ui.conf

clean:
	rm -rf build dist *.spec
	rm -f *.pyc
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: clean install
