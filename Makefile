#!/usr/bin/make -f

.DEFAULT_GOAL := build

DESTDIR ?=

build: clean
	uv run pyinstaller --onedir --name ns-admin \
	--add-data "src/ns2/assets:ns2/assets" \
	--collect-all nicegui \
	--hidden-import=dbus_next \
	--hidden-import=pam \
	--hidden-import=systemd src/ns2/ui/main.py

	$(MAKE) -C src/ns2/backend/ns

.PHONY: build

install:
	# Install the entire onedir build to /usr/lib/ns-admin
	install -d $(DESTDIR)/usr/lib/ns-admin
	cp -r dist/ns-admin/* $(DESTDIR)/usr/lib/ns-admin/

	# Ensure /usr/bin exists for symlinks
	install -d $(DESTDIR)/usr/bin

	# Install backend binary
	install -m 700 src/ns2/backend/ns/ns $(DESTDIR)/usr/lib/ns-admin/
	ln -sf /usr/lib/ns-admin/ns $(DESTDIR)/usr/bin/ns

	chmod 700 $(DESTDIR)/usr/lib/ns-admin

	# Symlink the executable to /usr/bin
	ln -sf /usr/lib/ns-admin/ns-admin $(DESTDIR)/usr/bin/ns-admin


	# Install config files
	install -D -m 644 configs/com.novus.ns.conf $(DESTDIR)/usr/share/dbus-1/system.d/com.novus.ns.conf
	install -D -m 644 configs/com.novus.ns.policy $(DESTDIR)/usr/share/polkit-1/actions/com.novus.ns.policy
	install -D -m 644 configs/ns-admin.xml $(DESTDIR)/usr/lib/firewalld/services/ns-admin.xml
	install -D -m 644 configs/ns2-ui.conf $(DESTDIR)/etc/nginx/sites-available/ns2-ui.conf

	install -D -m 644 configs/ns-admin.rules $(DESTDIR)/etc/polkit-1/rules.d/ns-admin.rules
	install -D -m 644 configs/10-firewalld.rules $(DESTDIR)/etc/polkit-1/rules.d/10-firewalld.rules
	install -D -m 644 configs/10-systemd1.rules $(DESTDIR)/etc/polkit-1/rules.d/10-systemd1.rules
	install -D -m 644 configs/10-nm.rules $(DESTDIR)/etc/polkit-1/rules.d/10-nm.rules


clean:
	rm -rf build dist *.spec
	rm -f *.pyc
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: clean install