#!/usr/bin/env python3.7
"""
::

  File:    buskill_gui.py
  Authors: Michael Altfield <michael@buskill.in>
  Created: 2020-06-23
  Updated: 2022-11-01
  Version: 0.4

This is the code to launch the BusKill GUI app

For more info, see: https://buskill.in/
"""

################################################################################
#                                   IMPORTS                                    #
################################################################################

import packages.buskill
from packages.garden.navigationdrawer import NavigationDrawer
from packages.garden.progressspinner import ProgressSpinner
from buskill_version import BUSKILL_VERSION

import os, sys, re, webbrowser

import multiprocessing, threading
from multiprocessing import util

import logging
logger = logging.getLogger( __name__ )
util.get_logger().setLevel(util.DEBUG)
multiprocessing.log_to_stderr().setLevel( logging.DEBUG )
#from multiprocessing import get_context

from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock

from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
Window.size = ( 300, 500 )

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.actionbar import ActionView
from kivy.uix.settings import Settings, SettingsWithNoMenu

# grey background color
Window.clearcolor = [ 0.188, 0.188, 0.188, 1 ]

from kivy.config import Config
from kivy.config import ConfigParser

from kivy.core.text import LabelBase

################################################################################
#                                  SETTINGS                                    #
################################################################################

# n/a

################################################################################
#                                   CLASSES                                    #
################################################################################

class MainWindow(Screen):

	toggle_btn = ObjectProperty(None)
	status = ObjectProperty(None)
	menu = ObjectProperty(None)
	actionview = ObjectProperty(None)
	actionbar = ObjectProperty(None)

	dialog = None

	def __init__(self, **kwargs):

		# check to see if this is an old version that was already upgraded
		# as soon as we've loaded
		Clock.schedule_once(self.handle_upgrades, 1)

		super(MainWindow, self).__init__(**kwargs)

	def on_pre_enter( self, *args ):

		msg = "DEBUG: User switched to 'MainWindow' screen"
		print( msg ); logger.debug( msg )

		# set the bk object to the BusKillApp's bk object
		# note we can't set this in __init__() because that's too early. the
		# 'root_app' instance field is manually set by the BusKillApp object
		# after this Screen instances is created but before it's added with
		# add_widget()
		self.bk = self.root_app.bk

	# called to close the app
	def close( self, *args ):
		sys.exit(0)

	def toggle_menu(self):

		self.nav_drawer.toggle_state()

	def toggle_buskill(self):

		self.bk.toggle()

		if self.bk.is_armed:
			self.toggle_btn.text = 'Disarm'
			self.status.text = 'BusKill is currently armed.'
			self.toggle_btn.background_color = self.color_red

			# set the actionview of every actionbar of every screen to red
			for screen in self.manager.screens:
				for child in screen.actionbar.children:
					if type(child) == ActionView:
						child.background_color = self.color_red

		else:
			self.toggle_btn.text = 'Arm'
			self.status.text = 'BusKill is currently disarmed.'
			self.toggle_btn.background_color = self.color_primary

			# set the actionview of every actionbar of every screen back to the
			# app's primary color
			for screen in self.manager.screens:
				for child in screen.actionbar.children:
					if type(child) == ActionView:
						child.background_color = self.color_primary

	def handle_upgrades( self, dt ):

		if self.bk.UPGRADED_TO:
			# the buskill app has already been updated; let's prompt the user to
			# restart to *that* version instead of this outdated version
			self.upgrade4_restart_prompt()

		# TODO: fix the restart on Windows so that the recursive delete after
		#       upgrade works and doesn't require a manual restart. See also:
		#  * packages/buskill/__init__()'s UPGRADED_FROM['DELETE_FAILED']
		#  * buskill_gui.py's upgrade5_restart()
		elif self.bk.UPGRADED_FROM and self.bk.UPGRADED_FROM['DELETE_FAILED']:
			# the buskill app was just updated, but it failed to delete the old
			# version. when this happens, we need the user to manually restart

			# close the dialog if it's already opened
			if self.dialog != None:
				self.dialog.dismiss()

			# open a new dialog that tells the user the error that occurred
			new_version_exe = bk.EXE_PATH
			msg = "To complete the update, this app must be manually restarted. Click to restart, then manually execute the new version at the following location.\n\n" + str(new_version_exe)
			self.dialog = DialogConfirmation(
			 title = '[font=mdicons][size=30]\ue923[/size][/font] Restart Required',
			 body = msg,
			 button = "",
			 continue_function=None
			)
			self.dialog.b_cancel.text = "Exit Now"
			self.dialog.b_cancel.on_release = self.close
			self.dialog.auto_dismiss = False
			self.dialog.open()

	def about_ref_press(self, ref):
		if ref == 'gui_help':
			return self.webbrowser_open_url( bk.url_documentation_gui )
		elif ref == 'contribute':
			return self.webbrowser_open_url( bk.url_documentation_contribute )

		return self.webbrowser_open_url( bk.url_website )

	def webbrowser_open_url(self, url ):
		msg = "DEBUG: Opening URL in webbrowser = " +str(url)
		print( msg ); logger.debug( msg )
		webbrowser.open( url )

	def about(self):

		# first close the navigation drawer
		self.nav_drawer.toggle_state()

		msg = "For latest news about BusKill, see our website at [ref=website][u]https://buskill.in[/u][/ref]\n\n"
		msg+= "For help, see our documentation at [ref=gui_help][u]https://docs.buskill.in[/u][/ref]\n\n"
		msg+= "Want to help? See [ref=contribute][u]contributing[/u][/ref]"

		self.dialog = DialogConfirmation(
		 title='BusKill ' +str(BUSKILL_VERSION['VERSION']),
		 body = msg,
		 button = "",
		 continue_function = None,
		)
		self.dialog.b_cancel.text = "OK"
		self.dialog.l_body.on_ref_press = self.about_ref_press
		self.dialog.open()

	def upgrade1(self):

		# first close the navigation drawer
		self.nav_drawer.toggle_state()

		# check to see if an upgrade was already done
		if self.bk.UPGRADED_TO and self.bk.UPGRADED_TO['EXE_PATH'] != '1':
			# a newer version has already been installed; skip upgrade() step and
			# just prompt the user to restart to the newer version
			msg = "DEBUG: Detected upgrade already installed " +str(self.bk.UPGRADED_TO)
			print( msg ); logger.debug( msg )
			self.upgrade4_restart_prompt()
			return

		msg = "Checking for updates requires internet access.\n\n"
		msg+= "Would you like to check for updates now?"

		self.dialog = DialogConfirmation(
		 title='Check for Updates?',
		 body = msg,
		 button='Check Updates',
		 continue_function=self.upgrade2,
		)
		self.dialog.open()

	def upgrade2(self):

		# close the dialog if it's already opened
		if self.dialog != None:
			self.dialog.dismiss()

		# open a new dialog with a spinning progress circle that tells the user
		# to wait for upgrade() to finish
		msg = "Please wait while we check for updates and download the latest version of BusKill."

		self.dialog = DialogConfirmation(
		 title='Updating BusKill',
		 body = msg,
		 button = "",
		 continue_function=None,
		)
		self.dialog.b_cancel.on_release = self.upgrade_cancel
		self.dialog.auto_dismiss = False

		progress_spinner = ProgressSpinner(
		 color = self.color_primary,
		)
		self.dialog.dialog_contents.add_widget( progress_spinner, 2 )
		self.dialog.dialog_contents.add_widget( Label( text='' ), 2 )
		self.dialog.size_hint = (0.9,0.9)

		self.dialog.open()

		# TODO: split this upgrade function into update() and upgrade() and
		# make the status somehow accessible from here so we can put it in a modal

		# Call the upgrade_bg() function which executes the upgrade() function in
		# an asynchronous process so it doesn't block the UI
		self.bk.upgrade_bg()

		# Register the upgrade3_tick() function as a callback to be executed
		# every second, and we'll use that to update the UI with a status
		# message from the upgrade() process and check to see if it the upgrade
		# finished running
		Clock.schedule_interval(self.upgrade3_tick, 1)

	# cancel the upgrade()
	def upgrade_cancel( self ):

		Clock.unschedule( self.upgrade3_tick )
		print( self.bk.upgrade_bg_terminate() )

	# this is the callback function that will be executed every one second
	# while buskill's upgrade() method is running
	def upgrade3_tick( self, dt ):
		print( "called upgrade3_tick()" )

		# update the dialog
		self.dialog.l_body.text = self.bk.get_upgrade_status()

		# did the upgrade process finish?
		if self.bk.upgrade_is_finished():
			# the call to upgrade() finished.
			Clock.unschedule( self.upgrade3_tick )

			try:
				self.upgrade_result = self.bk.get_upgrade_result()

			except Exception as e:
				# if the upgrade failed for some reason, alert the user

				# close the dialog if it's already opened
				if self.dialog != None:
					self.dialog.dismiss()

				# open a new dialog that tells the user the error that occurred
				self.dialog = DialogConfirmation(
				 title = '[font=mdicons][size=30]\ue002[/size][/font] Update Failed!',
				 body = str(e),
				 button = "",
				 continue_function=None
				)
				self.dialog.b_cancel.text = "OK"
				self.dialog.open()

				return

			# cleanup the pool used to launch upgrade() asynchronously asap
#			self.upgrade_pool.close()
#			self.upgrade_pool.join()

			# 1 = poll was successful; we're on the latest version
			if self.upgrade_result == '1':

				# close the dialog if it's already opened
				if self.dialog != None:
					self.dialog.dismiss()

				# open a new dialog that tells the user that they're already
				# running the latest version
				self.dialog = DialogConfirmation(
				 title = '[font=mdicons][size=30]\ue92f[/size][/font] Update BusKill',
				 body = "You're currently using the latest version",
				 button = "",
				 continue_function=None
				)
				self.dialog.b_cancel.text = "OK"
				self.dialog.open()
				return

			# if we made it this far, it means that the we successfully finished
			# downloading and installing the latest possible version, and the
			# result is the path to that new executable
			self.upgrade4_restart_prompt()

	def upgrade4_restart_prompt( self ):

		# close the dialog if it's already opened
		if self.dialog != None:
			self.dialog.dismiss()

		# open a new dialog that tells the user that the upgrade() was a
		# success and gets confirmation from the user to restart the app
		msg = "BusKill was updated successfully. Please restart this app to continue."
		self.dialog = DialogConfirmation(
		 title = '[font=mdicons][size=30]\ue92f[/size][/font]  Update Successful',
		 body = msg,
		 button='Restart Now',
		 continue_function = self.upgrade5_restart,
		)
		self.dialog.open()

	def upgrade5_restart( self ):

		if self.bk.UPGRADED_TO:
			new_version_exe = self.bk.UPGRADED_TO['EXE_PATH']
		else:
			new_version_exe = self.upgrade_result

		msg = "DEBUG: Exiting and launching " +str(new_version_exe)
		print( msg ); logger.debug( msg )

		# TODO: fix the restart on Windows so that the recursive delete after
		#       upgrade works and doesn't require a manual restart. See also:
		#  * packages/buskill/__init__()'s UPGRADED_FROM['DELETE_FAILED']
		#  * buskill_gui.py's handle_upgrades()
		try:

			# TODO: remove me (after fixing Windows restart fail)
			msg = 'os.environ|' +str(os.environ)+ "|\n"
			msg+= "DEBUG: os.environ['PATH']:|" +str(os.environ['PATH'])+  "|\n"
			print( msg ); logger.debug( msg )

			# cleanup env; remove references to now-old version
			oldVersionPaths = [
			 #os.path.split( sys.argv[0] )[0],
			 sys.argv[0].split( os.sep )[-2],
			 os.path.split( self.bk.APP_DIR )[1]
			]

			# TODO: remove me (after fixing Windows restart fail)
			msg = 'DEBUG: removing oldVersionPaths from PATH (' +str(oldVersionPaths)+ ')'
			print( msg ); logger.debug( msg )

			os.environ['PATH'] = os.pathsep.join( [ path for path in os.environ['PATH'].split(os.pathsep) if not re.match( ".*(" +"|".join(oldVersionPaths)+ ").*", path) ] )

			if 'SSL_CERT_FILE' in os.environ:
				del os.environ['SSL_CERT_FILE']

			# TODO: remove me (after fixing Windows restart fail)
			msg = 'os.environ|' +str(os.environ)+ "|\n"
			msg+= "DEBUG: os.environ['PATH']:|" +str(os.environ['PATH'])+  "|\n"
			print( msg ); logger.debug( msg )

			# replace this process with the newer version
			self.bk.close()
			os.execv( new_version_exe, [new_version_exe] )

		except Exception as e:

			msg = "DEBUG: Restart failed (" +str(e) + ")"
			print( msg ); logger.debug( msg )

			# close the dialog if it's already opened
			if self.dialog != None:
				self.dialog.dismiss()

			# open a new dialog that tells the user the error that occurred
			msg = "Sorry, we were unable to restart the BusKill App. Please execute it manually at the following location.\n\n" + str(new_version_exe)
			self.dialog = DialogConfirmation(
			 title = '[font=mdicons][size=30]\ue002[/size][/font] Restart Error',
			 body = msg,
			 button = "",
			 continue_function=None
			)
			self.dialog.b_cancel.text = "OK"
			self.dialog.open()

class DialogConfirmation(ModalView):

	title = StringProperty(None)
	body = StringProperty(None)
	button = StringProperty(None)
	continue_function = ObjectProperty(None)

	b_continue = ObjectProperty(None)

	def __init__(self, **kwargs):

		self._parent = None
		super(ModalView, self).__init__(**kwargs)

		if self.button == "":
			self.b_continue.parent.remove_widget( self.b_continue )
		else:
			self.b_continue.text = self.button

class CriticalError(BoxLayout):

	msg = ObjectProperty(None)

	def showError( self, msg ):
		self.msg.text = msg

	def fileBugReport( self ):
		# TODO: make this a redirect on buskill.in so old versions aren't tied
		#       to github.com
		webbrowser.open( 'https://docs.buskill.in/buskill-app/en/stable/support.html' )

class Settings(Screen):

	actionview = ObjectProperty(None)
	settings_content = ObjectProperty(None)

	def __init__(self, **kwargs):

		super(Settings, self).__init__(**kwargs)

	def on_pre_enter(self, *args):

		msg = "DEBUG: User switched to 'Settings' screen"
		print( msg ); logger.debug( msg )

		# set the bk object to the BusKillApp's bk object
		# note we can't set this in __init__() because that's too early. the
		# 'root_app' instance field is manually set by the BusKillApp object
		# after this Screen instances is created but before it's added with
		# add_widget()
		self.bk = self.root_app.bk

		# the "main" screen
		self.main_screen = self.manager.get_screen('main')

		# close the navigation drawer on the main screen
		self.main_screen.nav_drawer.toggle_state()

		# we steal (reuse) the instance field referencing the "modal dialog" from
		# the "main" screen
		self.dialog = self.main_screen.dialog

#	def on_enter(self):
#	def test_print(self):

		#s = Settings()
		#s.add_kivy_panel()
		#self.root_app.open_settings()

		#self.root_app.settings_cls = Settings

		#self.root_app.settings.add_kivy_panel()
		#s = self.root_app.create_settings( )
		print( "self.settings_content.children:|" +str(self.settings_content.children)+ "|" )

		# is the contents of 'settings_content' empty?
		if self.settings_content.children == []:
			# we haven't added the settings widget yet; add it now

			self.root_app.settings_cls = SettingsWithNoMenu
			s = self.root_app.settings_cls()

			self.root_app.build_settings(s)
			s.add_kivy_panel()

			print( "s:|" +str(s)+ "|" )
			print( "type(s):|" +str(type(s))+ "|" )
			print( "dir(s):|" +str(dir(s))+ "|" )
			print( "s.ids:|" +str(s.ids)+ "|" )
			print( "s.chlidren:|" +str(s.children)+ "|" )
			print( "s.properties:|" +str(s.properties)+ "|" )

			for child in s.children:
				print( "child:|" +str(child)+ "|" )

				for c in child.children:
					print( "\tc:|" +str(c)+ "|" )


				if type(child) == BoxLayout:
					print( "removing BoxLayout from child" )
					s.remove_widget(child) 

			#self.settings_content.add_widget( s )
			self.settings_content.add_widget( s )
			#settings_content.add_widget( Button() )

#	def test_print(self):
#		print( "====================================" )
#		print( self.root_app )
#		s = Settings()
#		self.root_app.settings_cls = SettingsWithNoMenu
#		#s = self.root_app.create_settings()
#		self.add_widget( s )

class DebugLog(Screen):

	debug_header = ObjectProperty(None)
	actionview = ObjectProperty(None)

	def __init__(self, **kwargs):

		self.show_debug_log_thread = None

		super(DebugLog, self).__init__(**kwargs)

	def on_pre_enter(self, *args):

		msg = "DEBUG: User switched to 'DebugLog' screen"
		print( msg ); logger.debug( msg )

		# set the bk object to the BusKillApp's bk object
		# note we can't set this in __init__() because that's too early. the
		# 'root_app' instance field is manually set by the BusKillApp object
		# after this Screen instances is created but before it's added with
		# add_widget()
		self.bk = self.root_app.bk

		# register the function for clicking the "help" icon at the top
		self.debug_header.bind( on_ref_press=self.ref_press )

		# the "main" screen
		self.main_screen = self.manager.get_screen('main')

		# close the navigation drawer on the main screen
		self.main_screen.nav_drawer.toggle_state()

		# we steal (reuse) the instance field referencing the "modal dialog" from
		# the "main" screen
		self.dialog = self.main_screen.dialog

		if logger.root.hasHandlers():
			self.logfile_path = logger.root.handlers[0].baseFilename

			with open(self.logfile_path) as log_file:
				self.debug_log_contents = log_file.read()

			# we use treading.Thread() instead of multiprocessing.Process
			# because it can update the widget's contents directly without
			# us having to pass data in-memory between the child process.
			# Con: We can't kill threads, so it should only be used for
			# short-running background tasks that won't get stuck
			self.show_debug_log_thread = threading.Thread(
			 target = self.show_debug_log
			)
			self.show_debug_log_thread.start()

	def show_debug_log( self ):
		lines = []
		for line in self.debug_log_contents.splitlines(keepends=False):
			lines.append({'text': line})
		self.rv.data = lines

	def copy_debug_log( self ):

		msg = "DEBUG: User copied contents of 'DebugLog' to clipboard"
		print( msg ); logger.debug( msg )

		Clipboard.copy( self.debug_log_contents )

		msg = "The full Debug Log has been copied to your clipboard.\n\n"
		self.dialog = DialogConfirmation(
		 title = '[font=mdicons][size=31]\ue88f[/size][/font] Debug Log',
		 body = msg,
		 button = "",
		 continue_function=None
		)
		self.dialog.b_cancel.text = "OK"
		self.dialog.l_body.bind( on_ref_press=self.ref_press )
		self.dialog.open()

	def go_back(self):
		self.manager.switch_to('main')

	def ref_press(self, widget, ref):

		# what did the user click?
		if ref == 'help_debug_log':
			# the user clicked the "help" icon; show them the help modal

			msg = "The Debug Log shows detailed information about the app's activity since it was started. This can be helpful to diagnose bugs if the app is not functioning as expected.\n\n"
			msg+= "For more info on how to submit a bug report, see [ref=bug_report][u]our documentation[/u][/ref]\n\n"
			msg+= "Your full Debug Log is stored in " +self.logfile_path+ "\n\n"
			self.dialog = DialogConfirmation(
			 title = '[font=mdicons][size=30]\ue88f[/size][/font] Debug Log',
			 body = msg,
			 button = "",
			 continue_function=None
			)
			self.dialog.b_cancel.text = "OK"
			self.dialog.l_body.bind( on_ref_press=self.ref_press )
			self.dialog.open()

		elif ref == 'bug_report':
			self.report_bug()

	def report_bug( self ):

		# for privacy reasons, we don't do in-app bug reporting; just point the
		# user to our documentation
		self.main_screen.webbrowser_open_url( self.bk.url_documentation_bug_report )

class BusKillApp(App):

	# copied mostly from 'site-packages/kivy/app.py'
	def __init__(self, bk, **kwargs):

		# instantiate our BusKill object instance so it can be accessed by
		# other objects for doing Buskill stuff
		self.bk = bk

		self._app_settings = None
		self._app_window = None
		super(App, self).__init__(**kwargs)
		self.options = kwargs
		self.built = False

	# instantiate our scren manager instance so it can be accessed by other
	# objects for changing the kivy screen
	manager = ScreenManager()

	# register font aiases so we don't have to specify their full file path
	# when setting font names in our kivy language .kv files
	LabelBase.register(
	 "Roboto",
	 #os.path.join( bk.EXE_DIR, 'fonts', 'Roboto-Regular.ttf' ), 
	 os.path.join( 'fonts', 'Roboto-Regular.ttf' ), 
	)
	LabelBase.register(
	 "RobotoMedium",
	 #os.path.join( bk.EXE_DIR, 'fonts', 'Roboto-Medium.ttf' ),
	 os.path.join( 'fonts', 'Roboto-Medium.ttf' ),
	)
	LabelBase.register(
	 "RobotoMono",
	 os.path.join( 'fonts', 'RobotoMono-Regular.ttf' ),
	)
	LabelBase.register(
	 "mdicons",
	 #os.path.join( bk.EXE_DIR, 'fonts', 'MaterialIcons-Regular.ttf' ),
	 os.path.join( 'fonts', 'MaterialIcons-Regular.ttf' ),
	)

	# does rapid-fire UI-agnostic cleanup stuff when the GUI window is closed
	def close( self, *args ):
		self.bk.close()

	def build_config(self, config):

		Config.read( self.bk.CONF_FILE )
		Config.setdefaults('buskill', {
		 'test1': 'value1',
		 'test2': '42'
		})	
		Config.set('kivy', 'exit_on_escape', '0')
		Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
		Config.write()

	def build(self):

		# this doesn't work in Linux, so instead we just overwrite the built-in
		# kivy icons with ours, but that's done in the linux build script
		#  * https://github.com/kivy/kivy/issues/2202
		self.icon = 'buskill-icon-150.png'

		# is the OS that we're running on supported?
		if self.bk.IS_PLATFORM_SUPPORTED:

			# yes, this platform is supported; show the main window
			Window.bind( on_request_close = self.close )

			# create all the Screens we need for our app
			screens = [
			 MainWindow(name='main'),
			 DebugLog(name='debug_log'),
			 Settings(name='settings'),
			]

			# loop through each screen created above
			for screen in screens:

				# assign an instance field named 'root_app' to each of our Screens
				# that references <this> BusKillApp object so that we can access
				# the App's instance fields (like 'bk') from within the Screen.
				# I know no built-in way to do this, since the root/parent of each
				# screen is None
				# 
				# Note: This must be done *before* adding the Screen to 'manager',
				# or the 'root_app' instance field will be unavailable in the
				# Screen's on_pre_load() functions
				screen.root_app = self

				# add the screen to the Screen Manager
				self.manager.add_widget( screen )

			return self.manager

		else:
			# the current platform isn't supported; show critical error window

			msg = buskill.ERR_PLATFORM_NOT_SUPPORTED
			print( msg ); logger.error( msg )

			crit = CriticalError()
			crit.showError( buskill.ERR_PLATFORM_NOT_SUPPORTED )
			return crit
