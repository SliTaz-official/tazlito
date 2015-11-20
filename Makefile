# Makefile for Tazlito.
# Check the README for more information.
#
SBINDIR?=/sbin
PREFIX?=/usr
DOCDIR?=/usr/share/doc
LINGUAS?=el es fr pl pt_BR ru zh_CN zh_TW

all:

# i18n.

pot:
	xgettext -o po/tazlito.pot -L Shell -k_ -k_n -k_p:1,2 \
		--package-name="TazLito" ./live.cgi ./tazlito-wiz

msgmerge:
	@for l in $(LINGUAS); do \
		echo -n "Updating $$l po file."; \
		msgmerge -U po/$$l.po po/tazlito.pot ; \
	done;

msgfmt:
	@for l in $(LINGUAS); do \
		echo "Compiling $$l mo file..."; \
		mkdir -p po/mo/$$l/LC_MESSAGES; \
		msgfmt -o po/mo/$$l/LC_MESSAGES/tazlito.mo po/$$l.po ; \
	done;

# Installation.
# Config file goes in /etc/tazlito

install: msgfmt
	install -m 0755 -d $(DESTDIR)$(PREFIX)/bin
	install -m 0777 tazlito $(DESTDIR)$(PREFIX)/bin
	-[ "$(VERSION)" ] && sed -i 's/^VERSION=[0-9].*/VERSION=$(VERSION)/' $(DESTDIR)$(PREFIX)/bin/tazlito
	ln -s tazlito $(DESTDIR)$(PREFIX)/bin/deduplicate
	ln -s tazlito $(DESTDIR)$(PREFIX)/bin/reduplicate
	install -m 0777 tazlito-wiz $(DESTDIR)$(PREFIX)/bin
	install -m 0755 -d $(DESTDIR)/etc/tazlito
	install -m 0644 tazlito.conf $(DESTDIR)/etc/tazlito
	install -m 0755 -d $(DESTDIR)/usr/share/doc
	install -m 0755 -d $(DESTDIR)/var/www/tazpanel/menu.d/boot
	install -m 0755 -d $(DESTDIR)/var/www/tazpanel/styles/default/images
	cp -a applications $(DESTDIR)/usr/share
	cp -a doc $(DESTDIR)/usr/share/doc/tazlito
	cp -a live.cgi $(DESTDIR)/var/www/tazpanel
	ln -s ../../live.cgi $(DESTDIR)/var/www/tazpanel/menu.d/boot/live
	cp -a tazlito.png $(DESTDIR)/var/www/tazpanel/styles/default/images
	# i18n
	mkdir -p $(DESTDIR)$(PREFIX)/share/locale
	cp -a po/mo/* $(DESTDIR)$(PREFIX)/share/locale

# Uninstallation commands.

uninstall:
	rm -f $(PREFIX)/bin/tazlito
	rm -f $(PREFIX)/bin/deduplicate
	rm -f $(PREFIX)/bin/reduplicate
	rm -f $(PREFIX)/bin/tazlito-wiz
	rm -f $(PREFIX)/var/www/tazpanel/menu.d/boot/live
	rm -f $(PREFIX)/var/www/tazpanel/styles/default/images/tazlito.png
	rm -f $(PREFIX)/var/www/tazpanel/live.cgi
	rm -rf $(PREFIX)/etc/tazlito
	rm -rf $(PREFIX)/usr/share/doc/tazlito
	rm -rf $(PREFIX)/usr/share/applications/tazlito*.desktop
	rm -rf $(PREFIX)/share/locale/*/LC_MESSAGES/tazlito.mo

clean:
	rm -rf po/mo
	rm -f po/*.mo
	rm -f po/*.*~
