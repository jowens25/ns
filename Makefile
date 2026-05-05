#!/usr/bin/make -f

.DEFAULT_GOAL := build

PYINSTALLER = uv run pyinstaller

PREFIX ?= /usr
DESTDIR ?=

build: clean
	$(PYINSTALLER) --onedir --name ns \
		--add-data "src/ns2/assets:ns2/assets" \
		--add-data "src/ns2/introspection:ns2/introspection" \
		--collect-all nicegui \
		--hidden-import=dbus_next \
		--hidden-import=pam \
		--hidden-import=plotly \
		--hidden-import=systemd \
		src/ns2/main.py

.PHONY: build

install: build
	# Install the entire onedir build to /usr/lib/ns
	install -d $(DESTDIR)$(PREFIX)/lib/ns
	cp -r dist/ns/* $(DESTDIR)$(PREFIX)/lib/ns/
	
	# Symlink the executable to /usr/bin
	install -d $(DESTDIR)$(PREFIX)/bin
	ln -sf $(PREFIX)/lib/ns/ns $(DESTDIR)$(PREFIX)/bin/ns
	
	# Install config files
	install -D -m 644 configs/com.novus.ns.conf $(DESTDIR)$(PREFIX)/share/dbus-1/system.d/com.novus.ns.conf
	install -D -m 644 configs/com.novus.ns.policy $(DESTDIR)$(PREFIX)/share/polkit-1/actions/com.novus.ns.policy
	install -D -m 644 configs/ns2.xml $(DESTDIR)$(PREFIX)/lib/firewalld/services/ns2.xml
	install -D -m 644 configs/ns2-ui.conf $(DESTDIR)/etc/nginx/sites-available/ns2-ui.conf
	install -D -m 644 configs/ns2.rules $(DESTDIR)/etc/polkit-1/rules.d/ns2.rules

clean:
	rm -rf build dist *.spec
	rm -f *.pyc
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: clean install
