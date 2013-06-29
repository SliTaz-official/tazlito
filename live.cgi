#!/bin/sh
#
# CGI interface for SliTaz Live systems using Tazlito and TazUSB.
#
# Copyright (C) 2011 SliTaz GNU/Linux - BSD License
#

if [ "$1" == "call" ]; then
	case "$2" in
	merge_cleanup)
		mv -f $3.merged $3
		for i in $4/*; do
			umount -d $i
		done
		rm -rf $4
		exit ;;
	esac
fi

# Common functions from libtazpanel
. lib/libtazpanel
get_config
header

TITLE=$(gettext 'TazPanel - Live')

# Build arguments to create a meta iso using 'tazlito merge' command
merge_args()
{
	tmp=$1
	first=true
	i=1
	while [ -n "$(GET input$i)" ]; do
		echo "$(stat -c "%s" $(GET input$i)) $(GET input$i) $(GET ram$i)"
		$((i++))
	done | sort -nr | while read size file ram; do
		if $first; then
			cp $file $(GET metaoutput)
			echo -n "$ram $(GET metaoutput) "
			first=false
			continue
		fi
		dir=$tmp/$(basename $file)
		mkdir $dir
		mount -o loop,ro $file $dir
		echo -n "$ram $dir/boot/rootfs.gz "
	done
}

#
# Commands executed in Xterm first
#

case " $(GET) " in
	*\ write_iso\ *)
		$TERMINAL $TERM_OPTS \
			-T "write-iso" \
			-e "tazlito writeiso $(GET write_iso)" & ;;
	*\ loramoutput\ *)
		$TERMINAL $TERM_OPTS \
			-T "build loram iso" \
			-e "tazlito build-loram $(GET input) $(GET loramoutput) $(GET type)" & ;;
	*\ meta\ *)
		tmp=/tmp/$(basename $0).$$
		cleanup="sh $0 call merge_cleanup $(GET output) $tmp"
		$TERMINAL $TERM_OPTS \
			-T "build meta iso" \
			-e "tazlito merge $(merge_args $tmp); \
				gettext 'ENTER to quit'; read i; \
				$cleanup" & ;;
	*\ hybrid\ *)
		$TERMINAL $TERM_OPTS \
			-T "build hybrid iso" \
			-e "iso2exe $(GET input)" & ;;
esac

#
# Commands
#

case " $(GET) " in
	*\ create\ *)
		#
		# Create a flavor file and ISO in options with all settings
		# Step by step interface and store files in cache.
		#
		gettext 'TODO' ;;
	*\ liveusb\ *)
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>$(gettext 'SliTaz LiveUSB')</h2>
	<p>$(gettext 'Create Live USB SliTaz systems')<p>
</div>

<p>$(gettext "Generate SliTaz LiveUSB media and boot in RAM! Insert a LiveCD \
into the cdrom drive, select the correct device and press Generate.")</p>

<form method="get" action="$SCRIPT_NAME">
	<input type="hidden" name="liveusb" />
	$(gettext 'USB Media to use:')
	<select name="gen">
EOT
		# List disk if there is a plugged USB device
		if [ -d /proc/scsi/usb-storage ]; then
			for i in `blkid | cut -d ":" -f 1`; do
				echo "<option value='$i'>$i</option>"
			done
		else
			echo "<option value="">$(gettext 'Not found')</option>"
		fi
		cat << EOT
	</select>
	<input type="submit" value="$(gettext 'Generate')" />
</form>
EOT
		if [ "$(GET gen)" ]; then
			cat << EOT
<h3>tazusb gen-liveusb $(GET gen)</h3>
<pre>
EOT
			# No pipe here so output is displayed in realtime
			yes | tazusb gen-liveusb $(GET gen)
			echo '</pre>'
		fi ;;
	*)
		#
		# Default xHTML content
		#
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>$(gettext 'SliTaz Live Systems')</h2>
	<p>$(gettext 'Create and manage Live CD or USB SliTaz systems')<p>
</div>

<div id="actions">
	<a class="button" href="$SCRIPT_NAME?liveusb">
		<img src="$IMAGES/harddisk.png" />$(gettext 'Create LiveUSB')</a>
</div>


<!--
<h3 id="livecd">$(gettext 'Write a Live CD')</h3>

<p>$(gettext "The command writeiso will generate an ISO image of the current \
filesystem as is, including all files in the /home directory. It is an easy \
way to remaster a SliTaz Live system, you just have to: boot, modify, \
writeiso.")</p>

<form method="get" action="$SCRIPT_NAME">
	$(gettext 'Compression type:')
	<select name="write_iso">
		<option value="gzip">gzip</option>
		<option value="lzma">lzma</option>
		<option value="none">$(gettext 'none')</option>
	</select>
	<input type="submit" value="$(gettext 'Write ISO')" />
</form> -->


<h3>$(gettext 'Live CD tools')</h3>

<h4 id="loram">$(gettext 'Convert ISO to loram')</h4>

<p>$(gettext "This command will convert an ISO image of a SliTaz Live CD to a \
new ISO image requiring less RAM to run.")</p>

<form method="get" action="$SCRIPT_NAME#loram">
	<table>
		<tr>
			<td>$(gettext 'ISO to convert')
				<input type="text" accept=".iso" name="input" value="/root/" /></td>
		</tr>
		<tr>
			<td><input type="radio" name="type" value="ram" id="type1" checked />
				<label for="type1">$(gettext 'The filesystem is always in RAM')</label>
			</td>
		</tr>
		<tr>
			<td><input type="radio" name="type" value="smallcdrom" id="type2" />
				<label for="type2">$(gettext 'The filesystem may be on a small CDROM')</label>
			</td>
		</tr>
		<tr>
			<td><input type="radio" name="type" value="cdrom" id="type3" />
				<label for="type3">$(gettext 'The filesystem may be on a large CDROM')</label>
			</td>
		</tr>
		<tr>
			<td>$(gettext 'ISO to create')
				<input type="text" accept=".iso" name="loramoutput" value="/root/loram.iso" />
			</td>
		</tr>
	</table>
	<input type="submit" value="$(gettext 'Convert ISO to loram')" />
</form>


<h4 id="hybrid">$(gettext 'Build a hybrid ISO')</h4>

<p>$(gettext "Add a master boot sector and a EXE header to the ISO image. \
")</p>

<form method="get" action="$SCRIPT_NAME#hybrid">
	<table>
	<tr>
	<td>
	$(gettext 'ISO to convert')
	<input type="text" name="input" value="/root/" />
	</td>
	</tr>
	</table>
	<input type="submit" name="hybrid" value="$(gettext 'Build a hybrid ISO')" />
</form>

<h4 id="meta">$(gettext 'Build a meta ISO')</h4>

<p>$(gettext "Combines several ISO flavors like nested Russian dolls. The \
amount of RAM available at startup will be used to select the utmost one.")</p>

<form method="get" action="$SCRIPT_NAME#meta">
	<table>
EOT
		i=""
		while [ -n "$(GET addmeta)" ]; do
			[ -n "$(GET input$i)" ] || break
			j=$(($i + 1))
			cat << EOT
		<tr>
			<td>$(gettext 'ISO number') $j: $(GET input$i)
				<input type="hidden" name="input$j" value="$(GET input$i)" />
			</td>
			<td>$(gettext 'Minimum RAM'): $(GET ram$i)
				<input type="hidden" name="ram$j" value="$(GET ram$i)" />
			</td>
		</tr>
EOT
			i=$j
		done
		metaoutput="$(GET metaoutput)"
		[ -n "$metaoutput" ] || metaoutput="/root/meta.iso"

		cat << EOT
		<tr>
			<td>$(gettext 'ISO to add')
				<input type="text" name="input" value="/root/" />
			</td>
			<td>$(gettext 'Minimum RAM')
				<input type="text" name="ram" value="128M" />
				<input type="submit" name="addmeta" value="$(gettext 'Add to the list')" />
			</td>
		</tr>
		<tr>
			<td>$(gettext 'ISO to create')
				<input type="text" name="metaoutput" value="$metaoutput" />
			</td>
		</tr>
	</table>
	<input type="submit" name="meta" value="$(gettext 'Build a meta ISO')" />
</form>

EOT
		;;
esac

xhtml_footer
exit 0
