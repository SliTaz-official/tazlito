#!/bin/sh
#
# CGI interface for SliTaz Live systems using Tazlito and TazUSB.
#
# Copyright (C) 2011-2015 SliTaz GNU/Linux - BSD License
#

if [ "$1" == 'call' ]; then
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


#------
# menu
#------

case "$1" in
	menu)
		TEXTDOMAIN_original="$TEXTDOMAIN"
		export TEXTDOMAIN='tazlito'
		cat <<EOT
<li><a data-icon="cd" href="live.cgi">$(_ 'Live')</a>
	<menu>
		<li><a data-icon="" href="live.cgi?liveusb" data-root>$(_ 'Create a live USB key')</a></li>
		<li><a data-icon="" href="live.cgi#liveiso" data-root>$(_ 'Create a live CD-ROM')</a></li>
		<li><a data-icon="" href="live.cgi#hybrid">$(_ 'Create a hybrid ISO')</a></li>
		<li><a data-icon="" href="live.cgi#loram" data-root>$(_ 'Convert ISO to loram')</a></li>
		<li><a data-icon="" href="live.cgi#meta" data-root>$(_ 'Build a meta ISO')</a></li>
	</menu>
</li>
EOT
		export TEXTDOMAIN="$TEXTDOMAIN_original"
		exit
esac


TEXTDOMAIN='tazlito'
TITLE=$(_ 'Live')
header


# Build arguments to create a meta iso using 'tazlito merge' command

merge_args() {
	tmp="$1"
	first=true
	i=1
	while [ -n "$(GET input$i)" ]; do
		echo "$(stat -c "%s" $(GET input$i)) $(GET input$i) $(GET ram$i)"
		$((i++))
	done | sort -nr | \
	while read size file ram; do
		if $first; then
			cp $file $(GET metaoutput)
			echo -n "$ram $(GET metaoutput) "
			first=false
			continue
		fi
		dir="$tmp/$(basename $file)"
		mkdir "$dir"
		mount -o loop,ro "$file" "$dir"
		echo -n "$ram $dir/boot/rootfs.gz "
	done
}


#
# Commands executed in Xterm first
#

case " $(GET) " in
	*\ loramoutput\ *)
		export output='raw'
		DISPLAY=':0.0' XAUTHORITY='/var/run/slim.auth' \
		$TERMINAL $TERM_OPTS \
			-T "$(_ 'Convert ISO to loram')" \
			-e "tazlito build-loram $(GET input) $(GET loramoutput) $(GET type)" &
		;;

	*\ meta\ *)
		tmp=/tmp/$(basename $0).$$
		cleanup="sh $0 call merge_cleanup $(GET output) $tmp"
		export output='raw'
		DISPLAY=':0.0' XAUTHORITY='/var/run/slim.auth' \
		$TERMINAL $TERM_OPTS \
			-T "$(_ 'Build a meta ISO')" \
			-e "tazlito merge $(merge_args $tmp); \
				_ 'ENTER to quit'; read i; \
				$cleanup" &
		;;

	*\ hybrid\ *)
		export output='raw'
		DISPLAY=':0.0' XAUTHORITY='/var/run/slim.auth' \
		$TERMINAL $TERM_OPTS \
			-T "$(_ 'Create a hybrid ISO')" \
			-e "iso2exe $(GET input)" &
		;;
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
		xhtml_header
		_ 'TODO'
		;;

	*\ liveusb\ *)
		TITLE="$(_ 'SliTaz LiveUSB')"
		xhtml_header "$(_ 'Create Live USB SliTaz systems')"
		cat <<EOT
<section>
	<header>$(_ 'SliTaz LiveUSB')</header>

	<form method="get" action="$SCRIPT_NAME" class="wide">
		<div>
$(_ "Generate SliTaz LiveUSB media and boot in RAM! Insert a Live CD \
into the CD-ROM drive, select the correct device and press Generate.")
		</div>

		<input type="hidden" name="liveusb" />
		<footer>
			$(_ 'USB Media to use:')
			<select name="gen" id="gen">
EOT
		# List disk if there is a plugged USB device
		if [ -d /proc/scsi/usb-storage ]; then
			for dev in /sys/block/sd*; do
				# removable writable sd* device:
				if [ "$(cat $dev/removable)" == '1' -a "$(cat $dev/ro)" == '0' ]; then
					echo "<optgroup label='$(cat $dev/device/vendor) $(cat $dev/device/model):'>"
					for part in $dev/sd*; do
						[ ! -d "$part" ] && break
						linuxdev=$(readlink -f /dev/block/$(cat $part/dev))
						cat <<EOT
<option value='$linuxdev'>$(basename $linuxdev) [$(blkid -o value -s TYPE "$linuxdev")]
 $(blkid -o value -s LABEL "$linuxdev") ($(cat $part/size | blk2h))</option>
EOT
					done
					echo '</optgroup>'
				fi
			done
		else
			echo "<option value=''>$(_ 'Not found')</option>"
		fi

		cat <<EOT
			</select>
			<button type="submit" data-icon="removable">$(_ 'Generate')</button>
		</footer>
	</form>
</section>
EOT

		gen="$(GET gen)"
		if [ -n "$gen" ]; then
			cat <<EOT
<script>document.getElementById("gen").value = "$gen";</script>

<section>
	<header>tazusb gen-liveusb $gen</header>
	<pre>
EOT
			# No pipe here so output is displayed in realtime
			yes | tazusb gen-liveusb $gen
		cat <<EOT
	</pre>
</section>
EOT
		fi

		;;

	*\ write_iso\ *)
		xhtml_header

		LaunchedByTazpanel="y" \
			tazlito writeiso $(GET write_iso) > /tmp/tazlitowriteiso 2>&1 &

		until [ -f /rootfs.gz ]; do
			sleep 1
		done
		cat <<EOT
<fieldset>
$(head /tmp/tazlitowriteiso | sed "s|$|<p></p>|g" | sed '/.gvfs/d')
<li id="fssize"> </li>
EOT
		until [ ! -f /rootfs.gz ]; do
			sleep 1
		cat <<EOT
<script type="text/javascript">
document.getElementById('fssize').innerHTML = "<h4>$(boldify $(du -mh /rootfs.gz | cut -f1))</h4>";
</script>
EOT
		done
		if [ -f /rootfs.gz ]; then
			until [ ! -f /rootfs.gz ]; do
				sleep 1
			done
		fi
		cat <<EOT
<script type="text/javascript">
document.getElementById('fssize').innerHTML = "$(boldify $(du -mh /home/slitaz/distro/rootcd/boot/rootfs.gz | cut -f1))";
</script>
/home/slitaz/distro/rootcd/boot/rootfs.gz
</fieldset>
EOT
		ls -l /home/slitaz/distro/rootcd/boot/rootfs.gz
		until [ -f /tmp/.write-iso* ]; do
			sleep 1
		done
		echo "<fieldset>"
		if	[ -f /tmp/.write-iso ]; then
			newline
			tail /tmp/tazlitowriteiso | grep ISO
			while [ -f /tmp/.write-iso ]; do sleep 1 ; done
		elif [ -f /tmp/.write-iso-error ]; then
			tail -n8 /tmp/tazlitowriteiso | grep -vE 'ENTER|----'
		fi
		tail -n5 /tmp/tazlitowriteiso | sed "s|$|<p></p>|g"
		ls -l /home/slitaz/distro
		echo "</fieldset>"
		echo "Use ' <code>tazlito emu-iso</code> ' to check it"
		;;

	*)
		#
		# Default xHTML content
		#
		TITLE="$(_ 'SliTaz Live Systems')"
		xhtml_header "$(_ 'Create and manage Live CD or USB SliTaz systems')"

		[ $(id -u) -eq 0 ] && cat <<EOT

<section id="liveiso">
	<header>$(_ 'Write a Live CD')</header>

	<form method="get" action="$SCRIPT_NAME" class="wide">
		<div>
$(_ "The command writeiso will generate an ISO image of the current \
filesystem as is, including all files in the /home directory. It is an easy \
way to remaster a SliTaz Live system, you just have to: boot, modify, \
writeiso.")
		</div>

		<table>
			<tr><td>
				$(_ 'Compression type:')
				<select name="write_iso">
					<option value="lzma">lzma</option>
					<option value="gzip">gzip</option>
					<option value="none">$(_ 'none')</option>
				</select>
			</td></tr>
		</table>
EOT

		if [ $(id -u) -eq 0 -a ! -d /media/cdrom/boot/isolinux -a ! -f /boot/*slitaz* ]; then
			msg warn "$(_ 'Cannot find SliTaz ISO/CD mounted in /media/cdrom (You will get only rootfs.gz)')"
		fi

		inputiso="$(GET input)"; inputiso="${inputiso:-/root/}"
		loramoutput="$(GET loramoutput)"; loramoutput="${loramoutput:-/root/loram.iso}"

		[ $(id -u) -eq 0 ] && cat <<EOT
		<footer>
			<button type="submit" data-icon="cd">$(_ 'Write ISO')</button>
		</footer>
	</form>
</section>


<section><header>$(_ 'Live CD tools')</header>


<section id="loram">
	<header>$(_ 'Convert ISO to loram')</header>

	<form method="get" action="$SCRIPT_NAME#loram" class="wide">
		<div>
$(_ "This command will convert an ISO image of a SliTaz Live CD to a \
new ISO image requiring less RAM to run.") (-30%)
		</div>

		<table>
			<tr><td>
				$(_ 'ISO to convert')
				<span id="input"><input type="text" name="input" value="$inputiso" /></span>
				<button data-icon="cd" onclick="ajax('index.cgi?do=file-selection&name=input', '1', 'input'); return false"/>
			</td></tr>
			<tr><td>
				<input type="radio" name="type" value="ram" id="type1" checked />
				<label for="type1">$(_ 'The filesystem is always in RAM')</label>
			</td></tr>
			<tr><td>
				<input type="radio" name="type" value="smallcdrom" id="type2" />
				<label for="type2">$(_ 'The filesystem may be on a small CD-ROM')</label>
			</td></tr>
			<tr><td>
				<input type="radio" name="type" value="cdrom" id="type3" />
				<label for="type3">$(_ 'The filesystem may be on a large CD-ROM')</label>
			</td></tr>
			<tr><td>
				$(_ 'ISO to create')
				<input type="text" accept=".iso" name="loramoutput" value="$loramoutput" />
			</td></tr>
		</table>

		<script>
EOT
		case "$(GET type)" in
			smallcdrom) sel='type2';;
			cdrom) sel='type3';;
			*) sel='type1';;
		esac
		[ $(id -u) -eq 0 ] echo "document.getElementById('$sel').checked = true;"
		[ $(id -u) -eq 0 ] && cat <<EOT
		</script>

		<footer>
			<button type="submit" data-icon="cd">$(_ 'Convert ISO to loram')</button>
		</footer>
	</form>
</section>

EOT
		cat <<EOT

<section id="hybrid">
	<header>$(_ 'Build a hybrid ISO')</header>

	<form method="get" action="$SCRIPT_NAME#hybrid" class="wide">
		<div>
$(_ "Add a master boot sector and an EXE header to the ISO image.")
		<ul>
<li>$(_ "Create a bootable image for a USB key, a memory card, a harddisk or a SSD.")</li>
<li>$(_ "With the .EXE suffix, it will run under DOS (16 bits) or Windows (32 bits).")</li>
<li>$(_ "Add the ISO filesystem md5 digest and the boot CRC in the ISO boot area.")</li>
<li>$(_ "Does not alter the ISO filesystem or the ISO image size.")</li>
		</ul>
		</div>

		<table>
			<tr><td>
				$(_ 'ISO to convert')
				<span id="input"><input type="text" name="input" /></span>
				<button data-icon="cd" onclick="ajax('index.cgi?do=file-selection&name=input', '1', 'input'); return false"/>
			</td></tr>
		</table>

		<footer>
			<button type="submit" name="hybrid" data-icon="cd">$(_ 'Build a hybrid ISO')</button>
		</footer>
	</form>
</section>

EOT
		[ $(id -u) -eq 0 ] && cat <<EOT

<section id="meta">
	<header>$(_ 'Build a meta ISO')</header>

	<form method="get" action="$SCRIPT_NAME#meta">
		<div>
$(_ "Combines several ISO flavors like nested Russian dolls. The \
amount of RAM available at startup will be used to select the utmost one.")
		</div>

		<table class="wide">
EOT
		i=''
		while [ -n "$(GET addmeta)" ]; do
			[ -n "$(GET input$i)" ] || break
			j=$(($i + 1))
			[ $(id -u) -eq 0 ] && cat <<EOT
			<tr>
				<td>
					$(_ 'ISO number %s:' "$j") $(GET input$i)
					<input type="hidden" name="input$j" value="$(GET input$i)" />
				</td>
				<td>
					$(_ 'Minimum RAM:') $(GET ram$i)
					<input type="hidden" name="ram$j" value="$(GET ram$i)" />
				</td>
			</tr>
EOT
			i=$j
		done
		metaoutput="$(GET metaoutput)"
		[ -n "$metaoutput" ] || metaoutput="/root/meta.iso"

		[ $(id -u) -eq 0 ] && cat <<EOT
			<tr>
				<td>
					$(_ 'ISO to add')
					<span id="input"><input type="text" name="input" value="/root/" /></span>
					<button data-icon="cd" onclick="ajax('index.cgi?do=file-selection&name=input', '1', 'input'); return false"/>
				</td>
				<td>
					$(_ 'Minimum RAM:')
					<input type="text" name="ram" value="128M" />
					<button type="submit" name="addmeta" value="addmeta" data-icon="add">$(_ 'Add to the list')</button>
				</td>
			</tr>
			<tr>
				<td>
					$(_ 'ISO to create')
					<input type="text" name="metaoutput" value="$metaoutput" />
				</td>
				<td>
				</td>
			</tr>
		</table>

		<footer>
			<button type="submit" name="meta" value="meta" data-icon="cd">$(_ 'Build a meta ISO')</button>
		</footer>
	</form>
</section>

</section>
EOT
		;;
esac

xhtml_footer
exit 0
