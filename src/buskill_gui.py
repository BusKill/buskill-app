#!/usr/bin/env python3
"""
::

  File:    buskill_gui.py
  Authors: Michael Altfield <michael@buskill.in>
  Created: 2020-06-23
  Updated: 2023-06-16
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

import os, sys, re, webbrowser, json, operator

import multiprocessing, threading
from multiprocessing import util

import logging
logger = logging.getLogger( __name__ )
util.get_logger().setLevel(util.DEBUG)
multiprocessing.log_to_stderr().setLevel( logging.DEBUG )
#from multiprocessing import get_context

import kivy
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.compat import string_types, text_type
from kivy.animation import Animation

from kivy.core.text import LabelBase
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window

Window.size = ( 300, 500 )

# grey background color
Window.clearcolor = [ 0.188, 0.188, 0.188, 1 ]

from kivy.config import Config
from kivy.config import ConfigParser

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.actionbar import ActionView
from kivy.uix.settings import Settings, SettingSpacer
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty, DictProperty
from kivy.uix.recycleview import RecycleView

################################################################################
#                                  SETTINGS                                    #
################################################################################

# n/a

################################################################################
#                                   CLASSES                                    #
################################################################################

# recursive function that checks a given object's parent up the tree until it
# finds the screen manager, which it returns
def get_screen_manager(obj):

	if hasattr(obj, 'manager') and obj.manager != None:
		return obj.manager

	if hasattr(obj, 'parent') and obj.parent != None:
		return get_screen_manager(obj.parent)

	return None

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
			self.status.text = "BusKill is armed\n"
			self.status.text += "with '" +str(self.bk.trigger)+ "' trigger."
			self.toggle_btn.background_color = self.color_red

			# set the actionview of every actionbar of every screen to red
			for screen in self.manager.screens:
				for child in screen.actionbar.children:
					if type(child) == ActionView:
						child.background_color = self.color_red

			# check for messages from the usb_handler child process
			Clock.schedule_interval( self.bk.check_usb_handler, 0.01 )

		else:
			self.toggle_btn.text = 'Arm'
			self.status.text = "BusKill is disarmed.\n"
			self.toggle_btn.background_color = self.color_primary

			# set the actionview of every actionbar of every screen back to the
			# app's primary color
			for screen in self.manager.screens:
				for child in screen.actionbar.children:
					if type(child) == ActionView:
						child.background_color = self.color_primary

			# stop checking for messages from the usb_handler child process
			Clock.unschedule( self.bk.check_usb_handler )

	def switchToScreen( self, screen ):
		self.manager.current = screen

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

###################
# SETTINGS SCREEN #
###################

# We heavily use (and expand on) the built-in Kivy Settings modules in BusKill
# * https://kivy-fork.readthedocs.io/en/latest/api-kivy.uix.settings.html
#
# Kivy's Settings module does the heavy lifting of populating the GUI Screen
# with Settings and Options that are defined in a json file, and then -- when
# the user changes the options for a setting -- writing those changes to a Kivy
# Config object, which writes them to disk in a .ini file.
#
# Note that a "Setting" is a key and an "Option" is a possible value for the
# Setting.
# 
# The json file tells the GUI what Settings and Options to display, but does not
# store state. The user's chosen configuration of those settings is stored to
# the Config .ini file.
#
# See also https://github.com/BusKill/buskill-app/issues/16

# We define our own BusKillOptionItem, which is an OptionItem that will be used
# by the BusKillSettingComplexOptions class below
class BusKillOptionItem(FloatLayout):

	title = StringProperty('')
	desc = StringProperty('')
	confirmation = StringProperty('')
	icon = StringProperty('')
	value = StringProperty('')
	parent_option = ObjectProperty()
	manager = ObjectProperty()

	def __init__(self, **kwargs):

		super(BusKillOptionItem, self).__init__(**kwargs)

	# this is called when the 'manager' Kivy Property changes, which will happen
	# some short time after __init__() when RecycleView creates instances of
	# this object
	def on_manager(self, instance, value):

		self.manager = value

		# the "main" screen
		self.main_screen = self.manager.get_screen('main')

		# we steal (reuse) the instance field referencing the "modal dialog" from
		# the "main" screen
		self.dialog = self.main_screen.dialog

	def on_parent_option(self, instance, value):
		print( "called on_parent_option()" )
		print( "instance.parent_option.value:|" +str(instance.parent_option.value)+ "|" )
		print( "instance.value:|" +str(instance.value)+ "|" )
		
		if instance.parent_option.value == instance.value :
			# this is the currenty-set option
			# set the radio button icon to "selected"
			#instance.radio_button_label.text = '[font=mdicons][size=18sp]\ue837[/size][/font] ' 
			instance.radio_button_label.text = 'F'
		else:
			# this is not the currenty-set option
			# set the radio button icon to "unselected"
			instance.radio_button_label.text = '[font=mdicons][size=18sp]\ue836[/size][/font] '

	# this is called when the user clicks on this OptionItem (eg choosing the
	# 'soft-shutdown' trigger)
	def on_touch_up( self, touch ):

		# skip this touch event if it wasn't *this* widget that was touched
		# * https://kivy.org/doc/stable/guide/inputs.html#touch-event-basics
		if not self.collide_point(*touch.pos):
			return

		# skip this touch event if it was actually a scroll event
		# * https://stackoverflow.com/questions/78183125/scrolling-causes-click-on-touch-up-event-on-widgets-in-kivy-recycleview
		if touch.button != "left":
			return

		# skip this touch event if they touched on an option that's already the
		# enabled option
		if self.parent_option.value == self.value:
			msg = "DEBUG: Option already equals '" +str(self.value)+ "'. Returning."
			print( msg ); logger.debug( msg )
			return

		# does this option have a warning to prompt the user to confirm their
		# selection before proceeding?
		if self.confirmation == "":
			# this option is safe; no confirmation is necessary
			self.enable_option()

		else:
			# this option can be dangerous; confirm with user before continuing

			self.dialog = DialogConfirmation(
			 title = '[font=mdicons][size=31]\ue002[/size][/font] Warning',
			 body = self.confirmation,
			 button='Continue',
			 continue_function=self.enable_option
			)
			self.dialog.b_cancel.text = "Cancel"
			self.dialog.open()
		
	# called when the user has chosen to change the setting to this option
	def enable_option( self ):

		if self.dialog != None:
			self.dialog.dismiss()

		# write change to disk in our persistant buskill .ini Config file
		key = str(self.parent_option.key)
		value = str(self.value)
		msg = "DEBUG: User changed config of '" +str(key) +"' to '" +str(value)+ "'"
		print( msg ); logger.debug( msg )

		Config.set('buskill', key, value)
		Config.write()

		# change the text of the option's value on the main Settings Screen
		self.parent_option.value = self.value

		# loop through every available option in the ComplexOption sub-Screen and
		# change the icon of the radio button (selected vs unselected) as needed
		for option in self.parent.children:

			# is this the now-currently-set option?
			if option.value == self.parent_option.value:
				# this is the currenty-set option
				# set the radio button icon to "selected"
				option.radio_button_label.text = "[font=mdicons][size=18]\ue837[/size][/font] "
			else:
				# this is not the currenty-set option
				# set the radio button icon to "unselected"
				option.radio_button_label.text = "[font=mdicons][size=18]\ue836[/size][/font] "

# We define our own BusKillSettingItem, which is a SettingItem that will be used
# by the BusKillSettingComplexOptions class below. Note that we don't have code
# here because the difference between the SettingItem and our BusKillSettingItem
# is what's defined in the buskill.kv file. that's to say, it's all visual
class BusKillSettingItem(kivy.uix.settings.SettingItem):
	pass

# Our BusKill app has this concept of a SettingItem that has "ComplexOptions"
#
# The closeset built-in Kivy SettingsItem type is a SettingOptions
#  * https://kivy-fork.readthedocs.io/en/latest/api-kivy.uix.settings.html#kivy.uix.settings.SettingOptions
#
# SettingOptions just opens a simple modal that allows the user to choose one of
# many different options for the setting. But for setting a BusKill trigger,
# we wanted a whole new screen so that we could have more space to tell the user
# what each trigger does, and also have a help button on the screen to describe
# what a trigger means. Also, the whole "New Screen for an Option" is more
# in-line with Material Design.
#  * https://m1.material.io/patterns/settings.html#settings-usage
#
# These are the reasons we create a special BusKillSettingComplexOptions class
class BusKillSettingComplexOptions(BusKillSettingItem):

	# each of these properties directly cooresponds to the key in the json
	# dictionary that's loaded with add_json_panel. the json file is what defines
	# all of our settings that will be displayed on the Settings Screen

	# icon defines the icon that's displayed on the Settings Screen for this
	# setting
	icon = ObjectProperty(None)

	# options is a parallel array of short names for different options for this
	# setting (eg 'lock-screen')
	options = ListProperty([])

	# options_long is a parallel array of short human-readable descriptions for
	# different options for this setting (eg 'BusKill will lock your screen')
	options_long = ListProperty([])

	# options_icons is a parallel array of icons for different options for this
	# setting. Note that this is distinct from the icon for the setting. the
	# 'icon' variable defined above is for the setting (eg 'trigger') while the
	# items in options_icons defines the icons for the options (possible values)
	# for that setting (eg 'lock-screen' or 'soft-shutdown')
	options_icons = ListProperty([])

	# confirmation is a parallel array of "confirmation messages" for the
	# different options for this setting. If a confirmation is set, then the user
	# will be presented with a popup message asking if they want to proceed
	# before the app will actually let them choose this option for this setting.
	# this is useful, for example, before they choose a possibly-dangerous option
	# (eg 'hard-shutdown'). If this is set to an empty string, then no
	# confirmation is presented to the user when they select this option
	confirmation = ListProperty([])

	def on_panel(self, instance, value):
		if value is None:
			return
		self.fbind('on_release', self._choose_settings_screen)

	def _choose_settings_screen(self, instance):

		manager = get_screen_manager(self)

		# create a new screen just for choosing the value of this setting, and
		# name this new screen "setting_<key>" 
		screen_name = 'setting_' +self.key

		# did we already create this sub-screen?
		if not manager.has_screen( screen_name ):
			# there is no sub-screen for this Complex Option yet; create it

			# create new screen for picking the value for this ComplexOption
			setting_screen = ComplexOptionsScreen(
			 name = screen_name
			)
		
			# define the help message that should appear when the user clicks the
			# help ActionButton on the top-right of the screen
			setting_screen.set_help_msg( self.desc )

			# set the color of the actionbar in this screen equal to whatever our
			# setting's screen actionbar is set to (eg blue or red)
			setting_screen.actionview.background_color = manager.current_screen.actionview.background_color

			# make the text in the actionbar match the 'title' for the setting as
			# it's defined in the settings json file
			setting_screen.set_actionbar_title( self.title )

			# loop through all possible values for this ComplexOption, zipping out
			# data from parallel arrays in the json file
			for value, desc, confirmation, icon in zip(self.options, self.options_long, self.confirmation, self.options_icons):

				# create an OptionItem for each of the possible values for this
				# setting option, and add them to the new ComplexOption sub-screen
				#option_item = BusKillOptionItem( title = self.key, value = value, desc = desc, confirmation = confirmation, icon = icon, parent_option = self, manager = manager )
				option_item = [{'title': self.key, 'value': value, 'icon':icon, 'desc': desc, 'confirmation': confirmation, 'parent_option': self, 'manager': manager }]
				#setting_screen.content.add_widget( option_item )
				setting_screen.rv.data.extend(option_item)

			# handle the "font" option
			if self.key == 'gui_font_face':
				# first we must determine what fonts are available on this system

				option_items = []
				font_paths = set()
				for fonts_dir_path in LabelBase.get_system_fonts_dir():

					for root, dirs, files in os.walk(fonts_dir_path):
						for file in files[0:10]:
							if file.lower().endswith(".ttf"):
								font_path = str(os.path.join(root, file))
								#print(font_path)
								font_paths.add( font_path )
								#option_item = BusKillOptionItem( self.key, font_path, 'desc', '', '', self, manager )
								#option_item = BusKillOptionItem( title = self.key, value = font_path, desc = 'test desc', confirmation = '', icon = '', parent_option = self, manager = manager )

								#setting_screen.content.add_widget( option_item )
								#setting_screen.rv.data = [{'text': str(x)} for x in range(4)]

				print( "Found " +str(len(font_paths))+ " font files." )

				for font_path in font_paths:
					font_filename = os.path.basename( font_path )
				
					option_items.append( {'title': 'title', 'value': font_filename, 'icon':'\ue167', 'desc':'', 'parent_option': self, 'manager': manager } )

				option_items.sort(key=operator.itemgetter('value'))
				print( "len(option_items):|" + str(len(option_items))+ "|" )
				print( "DEBUG: adding data:|" +str(option_items)+ "|" )
				setting_screen.rv.data.extend(option_items)

			# add the new ComplexOption sub-screen to the Screen Manager
			manager.add_widget( setting_screen )

		# change into the sub-screen now
		manager.transition.direction = 'left'
		manager.current = screen_name

# We define BusKillSettings (which extends the built-in kivy Settings) so that
# we can add a new type of Setting = 'commplex-options'). The 'complex-options'
# type becomes a new 'type' that can be defined in our settings json file
class BusKillSettings(kivy.uix.settings.Settings):

	def __init__(self, *args, **kargs):
		super(BusKillSettings, self).__init__(*args, **kargs)
		super(BusKillSettings, self).register_type('complex-options', BusKillSettingComplexOptions)

	def on_touch_down( self, touch ):
		super(BusKillSettings, self).on_touch_down(touch)

# Kivy's SettingsWithNoMenu is their simpler settings widget that doesn't
# include a navigation bar between differnt pages of settings. We extend that
# type with BusKillSettingsWithNoMenu so that we can use our custom
# BusKillSettings class (defined above) with our new 'complex-options' type
class BusKillSettingsWithNoMenu(BusKillSettings):

	def __init__(self, *args, **kwargs):
		self.interface_cls = kivy.uix.settings.ContentPanel
		super(BusKillSettingsWithNoMenu,self).__init__( *args, **kwargs )

		print( "init of BusKillSettingsWithNoMenu" )
		print( dir(self) )

	def on_touch_down( self, touch ):
		super(BusKillSettingsWithNoMenu, self).on_touch_down( touch )

# The ComplexOptionsScreen is a sub-screen to the Settings Screen. Kivy doesn't
# have sub-screens for defining options, but that's what's expected in Material
# Design. We needed more space, so we created ComplexOption-type Settings. And
# this is the Screen where the user transitions-to to choose the options for a
# ComplexOption
class ComplexOptionsScreen(Screen):

	actionview = ObjectProperty(None)
	settings_content = ObjectProperty(None)
	actionbar_title = ObjectProperty(None)
	help_msg = ObjectProperty(None)

	def set_help_msg(self, new_help_msg ):
		self.help_msg = new_help_msg

	def set_actionbar_title(self, new_title):
		self.actionbar_title = new_title

	def on_pre_enter(self, *args):

		msg = "DEBUG: User switched to '" +str(self.manager.current_screen.name)+ "' screen"
		print( msg ); logger.debug( msg )

		# the "main" screen
		self.main_screen = self.manager.get_screen('main')

		# close the navigation drawer on the main screen
		self.main_screen.nav_drawer.toggle_state()

		# we steal (reuse) the instance field referencing the "modal dialog" from
		# the "main" screen
		self.dialog = self.main_screen.dialog

	def show_help( self ):

		self.dialog = DialogConfirmation(
		 title = '[font=mdicons][size=30]\ue88f[/size][/font] ' + str(self.actionbar_title),
		 body = str(self.help_msg),
		 button = "",
		 continue_function=None
		)
		self.dialog.b_cancel.text = "OK"
		self.dialog.open()

# This is our main Screen when the user clicks "Settings" in the nav drawer
class BusKillSettingsScreen(Screen):

	actionview = ObjectProperty(None)

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

		# is the contents of 'settings_content' empty?
		if self.settings_content.children == []:
			# we haven't added the settings widget yet; add it now

			# kivy's Settings module is designed to use many different kinds of
			# "menus" (sidebars) for navigating different sections of the settings.
			# while this is powerful, it conflicts with the Material Design spec,
			# so we don't use it. Instead we use BusKillSettingsWithNoMenu, which
			# inherets kivy's SettingsWithNoMenu and we add sub-screens for
			# "ComplexOptions"; 
			s = BusKillSettingsWithNoMenu()
			s.root_app = self.root_app

			# create a new Kivy SettingsPanel using Config (our buskill.ini config
			# file) and a set of options to be drawn in the GUI as defined-by
			# the 'settings_buskill.json' file
			s.add_json_panel( 'buskill', Config, os.path.join(self.bk.SRC_DIR, 'packages', 'buskill', 'settings_buskill.json') )

			# our BusKillSettingsWithNoMenu object's first child is an "interface"
			# the add_json_panel() call above auto-pouplated that interface with
			# a bunch of "ComplexOptions". Let's add those to the screen's contents
			self.settings_content.add_widget( s )

	# called when the user leaves the Settings screen
	def on_pre_leave(self):
		# update runtime 'bk' instance with any settings changes, as needed

		# is the user going back to the main screen or some sub-Settings screen?
		if self.manager.current == "main":
			# the user is leaving the Settings screen to go back to the main Screen

			# attempt to re-arm BusKill if the trigger changed
			self.rearm_if_required()

	# called when the user clicks the "reset" button in the actionbar
	def reset_defaults(self):

		msg = "Are you sure you want to reset all your settings back to defaults?"

		self.dialog = DialogConfirmation(
		 title = '[font=mdicons][size=31]\ue002[/size][/font] Warning',
		 body = msg,
		 button='Erase Settings',
		 continue_function=self.reset_defaults2
		)
		self.dialog.b_cancel.text = "Cancel"
		self.dialog.open()

	# called when the user confirms they want to reset their settings
	def reset_defaults2(self):
		msg = "DEBUG: User initiated settings reset"
		print( msg ); logger.debug( msg )

		# close the dialog if it's already opened
		if self.dialog != None:
			self.dialog.dismiss()

		# delete all the options saved to the config file
		for key in Config['buskill']:
			Config.remove_option( 'buskill', key )
		Config.write()

		# setup the defaults again to avoid configparser.NoOptionError
		self.root_app.build_config(Config)

		# refresh all the values on the Settings Screen (and sub-screens)
		self.refresh_values()

	# updates the values of all the options on the Settings Screen and all
	# ComplexOptions sub-screens
	def refresh_values(self):

		# UPDATE SETTINGS SCREEN

		# loop through all the widgets on the Settings Screen
		for widget in self.settings_content.walk():

			# is this widget a BusKillSettingComplexOptions object?
			#if isinstance( widget, BusKillSettingComplexOptions ):
			if isinstance( widget, BusKillSettingComplexOptions ) \
			 or isinstance( widget, kivy.uix.settings.SettingBoolean ) \
			 or isinstance( widget, kivy.uix.settings.SettingNumeric ) \
			 or isinstance( widget, kivy.uix.settings.SettingOptions ) \
			 or isinstance( widget, kivy.uix.settings.SettingString ) \
			 or isinstance( widget, kivy.uix.settings.SettingPath ):

				# get the key for this SettingItem
				key = widget.key

				# get the value that the user has actually set this option to
				set_value = Config.get('buskill', key)

				# update the value for this SettingItem, which will update the text
				# in the Label on the Settings Screen
				widget.value = set_value

		# UPDATE SUB-SETTINGS SCREENS (for ComplexOptions)

		# loop through all of our sub-screens in the Settings screen (that are
		# used to change the values of ComplexOptions)
		for screen in self.manager.screens:

			# get the parent layout inside the screen and walk through all of its
			# child widgets
			parent_layout = screen.children[0]
			for widget in screen.walk():

				# is this widget a BusKillOptionItem?
				if isinstance( widget, BusKillOptionItem ):
					# yes, this is a radio button for an option; make sure it's set
					# correctly, depending on if it's selected or not in the config

					# get the title for this option (eg "trigger")
					title = widget.title

					# get the value that this particular radio button is for
					# (eg 'soft-shutdown')
					value = widget.value

					# get the value that the user has actually set this option to
					set_value = Config.get('buskill', title)

					# first, make sure that the parent of this option matches our
					# config
					widget.parent_option.value = set_value

					# is this the now-currently-set option?
					if value == set_value:
						# this is the currenty-set option
						# set the radio button icon to "selected"
						widget.radio_button_label.text = "[font=mdicons][size=18]\ue837[/size][/font] "
					else:
						# this is not the currenty-set option
						# set the radio button icon to "unselected"
						widget.radio_button_label.text = "[font=mdicons][size=18]\ue836[/size][/font] "

	# determine if we need to re-arm BusKill (eg if they changed the trigger
	# while BusKill is arm, we'd need to re-arm else it'll trigger not what the
	# user expects it to trigger)
	def rearm_if_required(self):

		# this changes to true if we have to disarm & arm BusKill again i norder to
		# apply the settings that the user changed
		rearm_required = False

		# trigger
		old_trigger = self.bk.trigger
		new_trigger = Config.get('buskill', 'trigger')

		# was the trigger just changed by the user?
		if old_trigger != new_trigger:
			# the trigger was changed; update the runtime bk instance
			self.bk.set_trigger( new_trigger )

			# is BusKill currently armed?
			if self.bk.is_armed == True:
				# buskill is currently armed; rearming is required to apply the change
				rearm_required = True

		# is it necessary to disarm and arm BusKill in order to apply the user's
		# changes to BusKill's settings?
		if rearm_required:
			msg = "DEBUG: Re-arm from '" +str(old_trigger)+ "' to '" +str(new_trigger)+ "' trigger?"
			print( msg ); logger.debug( msg )


			msg = "You've made changes to your settings that require disarming & arming again to apply."
			self.dialog = DialogConfirmation(
			 title = '[font=mdicons][size=30]\ue92f[/size][/font]  Apply Changes?',
			 body = msg,
			 button='Disarm & Arm Now',
			 continue_function = self.rearm
			)
			self.dialog.open()

	# re-arms BusKill
	def rearm(self):

		# close the dialog if it's already opened
		if self.dialog != None:
			self.dialog.dismiss()

		# turn it off and on again
		self.main_screen.toggle_buskill()
		self.main_screen.toggle_buskill()

#############
# DEBUG LOG #
#############

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

	msg = "DEBUG: Default font = " + str(Config.get('kivy', 'default_font'))
	print( msg ); logger.debug( msg )
	
	msg = "DEBUG: System fonts dir = " + str(LabelBase.get_system_fonts_dir())
	print( msg ); logger.debug( msg )

	# register font aiases so we don't have to specify their full file path
	# when setting font names in our kivy language .kv files
	try:
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
	except Exception as e:

		msg = "INFO: Failed to load fonts (" +str(e) + ")"
		print( msg ); logger.info( msg )

		try: 

			# find every font file in in all the font dirs
			font_paths = []
			for fonts_dir_path in LabelBase.get_system_fonts_dir():

				for root, dirs, files in os.walk(fonts_dir_path):
					for file in files:
						if file.lower().endswith(".ttf"):
							font_paths.append(str(os.path.join(root, file)))

			font_roboto_regular_path = [f for f in font_paths if f.lower().endswith("roboto-regular.ttf")]
			font_roboto_medium_path = [f for f in font_paths if f.lower().endswith("roboto-medium.ttf")]
			font_roboto_mono_path = [f for f in font_paths if f.lower().endswith("robotomono-regular.ttf")]
			font_mdicons_path = [f for f in font_paths if f.lower().endswith("materialicons-regular.ttf")]

			msg = "DEBUG: Found Roboto Regular " + str(font_roboto_regular_path)
			print( msg ); logger.debug( msg )
			msg = "DEBUG: Found Roboto Medium " + str(font_roboto_medium_path)
			print( msg ); logger.debug( msg )
			msg = "DEBUG: Found Roboto Mono " + str(font_roboto_mono_path)
			print( msg ); logger.debug( msg )
			msg = "DEBUG: Found Material Icons " + str(font_mdicons_path)
			print( msg ); logger.debug( msg )

			# just get the first file we found in all cases
			font_roboto_regular_path = font_roboto_regular_path[0]
			font_roboto_medium_path = font_roboto_medium_path[0]
			font_roboto_mono_path = font_roboto_mono_path[0]
			font_mdicons_path = font_mdicons_path[0]

			LabelBase.register(
			 "Roboto",
			 font_roboto_regular_path
			)
			LabelBase.register(
			 "RobotoMedium",
			 font_roboto_medium_path
			)
			LabelBase.register(
			 "RobotoMono",
			 font_roboto_mono_path
			)
			LabelBase.register(
			 "mdicons",
			 font_mdicons_path
			)

		except Exception as e:

			msg = "WARNING: Failed to find fonts (" +str(e) + ")"
			print( msg ); logger.warning( msg )


	# does rapid-fire UI-agnostic cleanup stuff when the GUI window is closed
	def close( self, *args ):
		self.bk.close()

	def build_config(self, config):

		Config.read( self.bk.CONF_FILE )
		Config.setdefaults('buskill', {
		 'trigger': 'lock-screen',
		 'gui_font_face': None,
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
			 BusKillSettingsScreen(name='settings'),
			]

			# loop through each screen created above
			for screen in screens:
				msg = "DEBUG: adding screen:|" +str(screen)+ "|"
				print( msg ); logger.debug( msg )

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
