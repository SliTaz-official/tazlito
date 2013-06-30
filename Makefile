# Makefile for Tazlito.
# Check the README for more information.
#
SBINDIR?=/sbin
PREFIX?=/usr
DOCDIR?=/usr/share/doc
LINGUAS?=el es_AR fr pt_BR

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
	install -m 0755 -d $(DESTDIR)$(PREFIX)/bin
	install -m 0777 tazlito $(DESTDIR)$(PREFIX)/bin
	install -m 0777 tazlito-wiz $(DESTDIR)$(PREFIX)/bin
	install -m 0755 -d $(DESTDIR)/etc/tazlito
	install -m 0644 tazlito.conf $(DESTDIR)/etc/tazlito
	install -m 0755 -d $(DESTDIR)/usr/share/doc
	install -m 0755 -d $(DESTDIR)/var/www/tazpanel/menu.d/boot
	install -m 0755 -d $(DESTDIR)/var/www/tazpanel/styles/default/images
	cp -a applications $(DESTDIR)/usr/share
	cp -a doc $(DESTDIR)/usr/share/doc/tazlito
	cp -a live.cgi $(DESTDIR)/var/www/tazpanel
	cp -a live $(DESTDIR)/var/www/tazpanel/menu.d/boot
	cp -a tazlito.png $(DESTDIR)/var/www/tazpanel/styles/default/images
	# i18n
	mkdir -p $(DESTDIR)$(PREFIX)/share/locale
	cp -a po/mo/* $(DESTDIR)$(PREFIX)/share/locale

# Uninstallation commands.

uninstall:
	rm -f $(PREFIX)/bin/tazlito
	rm -f $(PREFIX)/bin/tazlito-wiz
	rm -f $(PREFIX)/var/www/tazpanel/menu.d/boot/live
	rm -f $(PREFIX)/var/www/tazpanel/styles/default/images/tazlito.png
	rm -f $(PREFIX)/var/www/tazpanel/live.cgi
	rm -rf $(PREFIX)/etc/tazlito
	rm -rf $(PREFIX)/usr/share/doc/tazlito
	rm -rf $(PREFIX)/usr/share/applications/tazlito*.desktop
	rm -rf $(PREFIX)/share/locale/*/LC_MESSAGES/tazlito*.mo

clean:
	rm -rf po/mo
	rm -f po/tazlito-wiz/*.mo
	rm -f po/tazlito-wiz/*.*~
