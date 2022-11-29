.. _test_app:

Testing buskill-app
====================

This section documents how to test the BusKill App.

.. note::

  Currently we don't have any automated tests. While we'd like to change that, it's not clear how to simulate USB hotplug events in automated tests. Progress on this research can be found here:

 * https://github.com/BusKill/buskill-app/issues/32
 * https://github.com/BusKill/buskill-app/issues/38
 * https://stackoverflow.com/questions/74090470/simulating-a-hotplug-event-with-libusb-test-debugging

Linux
-----

Because of how easy it is to quickly "install" and launch various Linux distributions in a new docker container, Linux is the easiest platform on which to test the BusKill app.

.. note::

  Currently it's not possible to automate these tests on GitHub because nested virtualization is not available on shared GitHub Runners. For more info, see

 * https://github.com/BusKill/buskill-app/issues/32#issuecomment-1207248758
 * https://github.com/actions/runner-images/issues/183

On a machine that supports nested virtualization (eg your laptop), execute the following commands to launch the BusKill app in CLI mode on a dozen or so different Linux distributions (Note: Replace BUSKILL_RELEASE_URL with a link to the release you'd like to test).

::

	sudo apt-get install docker.io
	sudo bash -c 'gpasswd -a "${SUDO_USER}" docker'
	su - `whoami`

	BUSKILL_RELEASE_URL='https://github.com/BusKill/buskill-app/releases/download/3309700248_linux/buskill-lin-v0.6.0-x86_64.tbz'
	DOCKER_IMAGES='ubuntu:14.04 ubuntu:16.04 ubuntu:18.04 ubuntu:20.04 ubuntu:22.04 debian:oldstable-slim debian:stable-slim fedora:35 fedora:36 fedora:37'

	tmpDir=`mktemp -d`
	pushd "${tmpDir}"

	wget "${BUSKILL_RELEASE_URL}"
	tar -xjvf buskill-lin-*.tbz
	buskill_release_dir=`find "${tmpDir}" -mindepth 1 -maxdepth 1 -type d`

	# create script for this iteration of the loop
	cat > "runInDockerContainer.sh" <<EOF
	#!/bin/bash
	apt-get update
	apt-get install -y libfuse2 libusb-1.0-0-dev
	/root/buskill-app/buskill-*/buskill-*.AppImage --arm
	EOF
	chmod +x runInDockerContainer.sh

	for image in ${DOCKER_IMAGES}; do

		# create script for this iteration of the loop
		script_path="${image}.sh"
		cat > "${script_path}" <<EOF
		echo ${image}
		
		cd "${buskill_release_dir}"
		export DOCKER_CONTENT_TRUST=1
		docker run --privileged --rm --net host -v /run/udev/control:/run/udev/control -v "`pwd`:/root/buskill-app" -it ${image} /root/buskill-app/runInDockerContainer.sh
		
		read waiting
	EOF
		chmod +x "${script_path}"

		x-terminal-emulator -e bash ${script_path} & 
	done

Windows
-------

Linux users can test on Windows by running Windows in a VM. Microsoft provides free downloads of Windows 10 for 90-days for testing purposes, which can be found here:

 * https://www.microsoft.com/en-us/evalcenter/evaluate-windows-10-enterprise

If you're struggling to get USB passthrough to work in you VM software (eg Xen, VMWare, VirtualBox, etc), you can instead create a "Virtual Hard Drive" using built-in Microsoft tools. Mounting the VHD will cause a USB Hotplug event. Removing the VHD will cause a USB Hotplug Removal event, which will simulate the removal of the BusKill cable and cause the BusKill app to execute the trigger.

To create a new VHD on Windows 10:

#. Click inside "Type here to search"
#. Type "Disk Management"
#. Click on "Create and format hard disk partitions"
#. On the new window, click "Action" -> "Create VHD"
#. Click "Browse"
#. Type "BusKill" for "Location" to create a file named "BusKill.vhd"
#. Click "Save"
#. Type "10" for "Virtual hard disk size" (to create a 10 MB VHD)
#. Click "OK"
#. Click "Action" -> "Attach VHD"
#. Click "Browse"
#. Click "BusKill.vhd"
#. Click "Open"
#. Click "OK"
#. Scroll-down in the bottom-half of the "Disk Management" window, and right-click the left part of the new 10 MB "Unknown" disk. Select "Initalize Disk"
#. Click "OK"
#. Right-click the right part of the new disk (9 MB Unallocated). Select "New Simple Volume".
#. Click "Next". Click "Next". Click "Next". Click "Next". Click "Finish".
#. Open Windows Explorer and go to "This PC". You'll see a "New Volume".

You can now open the BusKill app and arm it. If you eject the "New Volume" (right click it and select "Eject", then the BusKill app will execute the configured trigger.

You can re-attach the VHD by opening "Disk Management" and going to "Action" -> "Attach VHD"

MacOS
-----

Apple is very hostile to developers, and they don't make it easy run MacOS in a VM on Linux.

If you know of a way to:

#. Easily run MacOS in a VM, and/or
#. Simulate USB hotplug events in a headless machine running MacOS

...then please do `contact us <https://buskill.in/contact/>`_.

Fortunately, the BusKill project is `sponsored by Mac Stadium <https://www.macstadium.com/opensource>`_. They donated a Mac Mini to us, which runs in their cloud. We tunnel VNC through SSH and use it to test the BusKill app.

.. note::

	We don't know of any way to simulate USB Hotplug events on MacOS, so we just use the ``--run-trigger`` argument to the BusKill app to confirm that our triggers on MacOS work.

If you have a machine running MacOS, one simple thing you can do to :ref:`help the BusKill project<contributing>` is offer to test new releases on MacOS. If you'd like to help us test BusKill on MacOS, please `contact us <https://buskill.in/contact/>`_.
