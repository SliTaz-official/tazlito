# Makefile for Tazlito.
# Check the README for more informations.
#
SBINDIR?=/sbin
PREFIX?=/usr
DOCDIR?=/usr/share/doc

all:

# Installation.
# Config file goes in /etc/tazlito

install:
	@echo "Installing Tazlito into $(PREFIX)/bin..."
	install -g root -o root -m 0777 tazlito $(PREFIX)/bin
	install -g root -o root -m 0755 -d /etc/tazlito
	install -g root -o root -m 0644 tazlito.conf /etc/tazlito
	#install -g root -o root -m 0644 distro-packages.list /etc/tazlito
	@echo "Installing Tazlito documentation..."
	install -g root -o root -m 0755 -d /usr/share/doc/tazlito
	install -g root -o root -m 0644 doc/tazlito.html /usr/share/doc/tazlito

# Uninstallation commands.

uninstall:
	rm -f $(PREFIX)/bin/tazlito
	rm -rf /etc/tazlito
	rm -rf /usr/share/doc/tazlito

