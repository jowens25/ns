#!/usr/bin/make -f

.DEFAULT_GOAL := build

NICEGUI_PACK = uv run nicegui-pack

# Define output target
APP_TARGET = dist/ns-admin

PREFIX ?= /usr
DESTDIR ?=

build:
	$(NICEGUI_PACK) --onedir --name ns-admin \
		--add-data "src/ns_admin/assets:ns_admin/assets" \
		--add-data "src/ns_admin/introspection:ns_admin/introspection" \
		src/ns_admin/main.py

.PHONY: build

install: build
	# Install the entire onedir build to /usr/lib/ns-admin
	install -d $(DESTDIR)$(PREFIX)/lib/ns-admin
	cp -r dist/ns-admin/* $(DESTDIR)$(PREFIX)/lib/ns-admin/
	
	# Symlink the executable to /usr/bin
	install -d $(DESTDIR)$(PREFIX)/bin
	ln -sf $(PREFIX)/lib/ns-admin/ns-admin $(DESTDIR)$(PREFIX)/bin/ns-admin
	
	# Install config files
	install -D -m 644 configs/com.novus.ns.conf $(DESTDIR)$(PREFIX)/share/dbus-1/system.d/com.novus.ns.conf 
	install -D -m 644 configs/ns2.xml $(DESTDIR)$(PREFIX)/lib/firewalld/services/ns2.xml
	install -D -m 644 configs/ns2-ui.conf $(DESTDIR)/etc/nginx/sites-available/ns2-ui.conf

clean:
	rm -rf build dist *.spec
	rm -f *.pyc
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: clean install
