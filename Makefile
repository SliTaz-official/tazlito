# Makefile for Tazlito.
# Check the README for more information.
#
SBINDIR?=/sbin
PREFIX?=/usr
DOCDIR?=/usr/share/doc
LINGUAS?=

all:

# i18n.

pot:
	xgettext -o po/tazlito-wiz/tazlito-wiz.pot -L Shell \
		--package-name="TazLito Wiz" ./tazlito-wiz

msgmerge:
	@for l in $(LINGUAS); do \
		echo -n "Updating $$l po file."; \
		msgmerge -U po/tazlito-wiz/$$l.po po/tazlito-wiz/tazlito-wiz.pot ; \
	done;

msgfmt:
	@for l in $(LINGUAS); do \
		echo "Compiling $$l mo file..."; \
		mkdir -p po/mo/$$l/LC_MESSAGES; \
		msgfmt -o po/mo/$$l/LC_MESSAGES/tazlito-wiz.mo po/tazlito-wiz/$$l.po ; \
	done;

# Installation.
# Config file goes in /etc/tazlito

install: msgfmt
	@echo "Installing Tazlito into $(PREFIX)/bin..."
	install -g root -o root -m 0777 tazlito $(PREFIX)/bin
	install -g root -o root -m 0777 tazlito-wiz $(PREFIX)/bin
	install -g root -o root -m 0755 -d /etc/tazlito
	install -g root -o root -m 0644 tazlito.conf /etc/tazlito
	@echo "Installing Tazlito documentation..."
	install -g root -o root -m 0755 -d /usr/share/doc/tazlito
	install -g root -o root -m 0644 doc/*.html /usr/share/doc/tazlito
	# i18n
	mkdir -p $(DESTDIR)$(PREFIX)/share/locale
	cp -a po/mo/* $(DESTDIR)$(PREFIX)/share/locale

# Uninstallation commands.

uninstall:
	rm -f $(PREFIX)/bin/tazlito
	rm -f $(PREFIX)/bin/tazlito-wiz
	rm -rf /etc/tazlito
	rm -rf /usr/share/doc/tazlito
	rm -rf $(DESTDIR)$(PREFIX)/share/locale/*/LC_MESSAGES/tazlito*.mo

clean:
	rm -rf _pkg
	rm -rf po/mo
	


