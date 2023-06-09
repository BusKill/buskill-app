#!/usr/bin/env python3
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

import os, sys, re, webbrowser, json

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
	print( "obj:|" +str(obj)+ "|" )

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

		# TODO: remove auto-switch to Settings screen
		#Clock.schedule_once( lambda dt: self.switchToScreen('settings') )

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
			self.status.text = "BusKill is currently armed\n"
			self.status.text += "with '" +str(self.bk.trigger)+ "' trigger."
			self.toggle_btn.background_color = self.color_red

			# set the actionview of every actionbar of every screen to red
			for screen in self.manager.screens:
				for child in screen.actionbar.children:
					if type(child) == ActionView:
						child.background_color = self.color_red

		else:
			self.toggle_btn.text = 'Arm'
			self.status.text = "BusKill is currently disarmed.\n"
			self.toggle_btn.background_color = self.color_primary

			# set the actionview of every actionbar of every screen back to the
			# app's primary color
			for screen in self.manager.screens:
				for child in screen.actionbar.children:
					if type(child) == ActionView:
						child.background_color = self.color_primary

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

class BusKillOptionItem(FloatLayout):

	def __init__(self, title, desc, confirmation, icon, parent_option, manager, **kwargs):

		self.title = title
		self.desc = desc
		self.confirmation = confirmation
		self.icon = icon
		#self.value = current_value
		self.value = 'replaceme'
		self.parent_option = parent_option
		self.manager = manager
		print( "self.manager:|" +str(self.manager)+ "|" )

		# the "main" screen
		self.main_screen = self.manager.get_screen('main')

		# we steal (reuse) the instance field referencing the "modal dialog" from
		# the "main" screen
		self.dialog = self.main_screen.dialog

		super(BusKillOptionItem, self).__init__(**kwargs)

	def on_touch_up( self, touch ):

		# skip this touch event if it wasn't *this* widget that was touched
		# * https://kivy.org/doc/stable/guide/inputs.html#touch-event-basics
		if not self.collide_point(*touch.pos):
			return

		print()
		print( "called BusKillOptionItem.on_touch_up()" )
		print( "self:|" +str(self)+ "|" )
		print( "self.parent:|" +str(self.parent)+ "|" )
		print( "dir(self.parent):|" +str(dir(self.parent))+ "|\n" )
		print( "self.parent_option:|" +str(self.parent_option)+ "|" )
		print( "dir(self.parent_option):|" +str(dir(self.parent_option))+ "|\n" )
		print()

		#print( "self.value:|" +str(self.value)+ "|" )
		print( "value:|" +str(self.parent_option.value)+ "|" )
		print( "self.title:|" +str(self.title)+ "|" )
		print( "self.desc:|" +str(self.desc)+ "|" )
		print( "self.confirmation:|" +str(self.confirmation)+ "|" )
		print( "dir(self):|" +str(dir(self))+ "|\n" )

		print( "self.parent:|" +str(self.parent)+ "|" )
		print( "self.parent.children:|" +str(self.parent.children)+ "|" )

		# TODO: if there's a confirmation, don't continue until they confirm
		print( "self.confirmation:|" +str(self.confirmation)+ "|" )

		# skip this touch event if they touched on an option that's already the
		# enabled option
		if self.parent_option.value == self.title:
			print( "self.parent_option.value equals self.title. Returning now" )
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
			#self.dialog.l_body.bind( on_ref_press=self.ref_press )
			self.dialog.open()
		
	def enable_option( self ):

		if self.dialog != None:
			self.dialog.dismiss()

		# write change to disk in our persistant buskill .ini Config file
		key = str(self.parent_option.key)
		value = str(self.title)
		msg = "DEBUG: User changed config of '" +str(key) +"' to '" +str(value)+ "'"
		print( msg ); logger.debug( msg )

		Config.set('buskill', key, value)
		Config.write()

		self.parent_option.value = self.title
		parent = self.parent
		for option in self.parent.children:
			#print( "option:|" +str(option)+ "|" )
			#print( "option.title:|" +str(option.title)+ "|" )
			#print( "removing " +str(option.title)+ " from " +str(self.parent) )
			#parent.remove_widget(option)
			#parent.add_widget(option)
			if option.title == self.parent_option.value:
				option.radio_button_label.text = "[font=mdicons][size=18]\ue837[/size][/font]"
			else:
				option.radio_button_label.text = "[font=mdicons][size=18]\ue836[/size][/font]"

		#print( "touch:|" +str(touch)+ "|" )

class BusKillSettingItem(kivy.uix.settings.SettingItem):

    '''Base class for individual settings (within a panel). This class cannot
    be used directly; it is used for implementing the other setting classes.
    It builds a row with a title/description (left) and a setting control
    (right).

    Look at :class:`SettingBoolean`, :class:`SettingNumeric` and
    :class:`SettingOptions` for usage examples.

    :Events:
        `on_release`
            Fired when the item is touched and then released.

    '''

    title = StringProperty('<No title set>')
    '''Title of the setting, defaults to '<No title set>'.

    :attr:`title` is a :class:`~kivy.properties.StringProperty` and defaults to
    '<No title set>'.
    '''

    desc = StringProperty(None, allownone=True)
    '''Description of the setting, rendered on the line below the title.

    :attr:`desc` is a :class:`~kivy.properties.StringProperty` and defaults to
    None.
    '''

    disabled = BooleanProperty(False)
    '''Indicate if this setting is disabled. If True, all touches on the
    setting item will be discarded.

    :attr:`disabled` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.
    '''

    section = StringProperty(None)
    '''Section of the token inside the :class:`~kivy.config.ConfigParser`
    instance.

    :attr:`section` is a :class:`~kivy.properties.StringProperty` and defaults
    to None.
    '''

    key = StringProperty(None)
    '''Key of the token inside the :attr:`section` in the
    :class:`~kivy.config.ConfigParser` instance.

    :attr:`key` is a :class:`~kivy.properties.StringProperty` and defaults to
    None.
    '''

    value = ObjectProperty(None)
    '''Value of the token according to the :class:`~kivy.config.ConfigParser`
    instance. Any change to this value will trigger a
    :meth:`Settings.on_config_change` event.

    :attr:`value` is an :class:`~kivy.properties.ObjectProperty` and defaults
    to None.
    '''

    panel = ObjectProperty(None)
    '''(internal) Reference to the SettingsPanel for this setting. You don't
    need to use it.

    :attr:`panel` is an :class:`~kivy.properties.ObjectProperty` and defaults
    to None.
    '''

    content = ObjectProperty(None)
    '''(internal) Reference to the widget that contains the real setting.
    As soon as the content object is set, any further call to add_widget will
    call the content.add_widget. This is automatically set.

    :attr:`content` is an :class:`~kivy.properties.ObjectProperty` and defaults
    to None.
    '''

    selected_alpha = NumericProperty(0)
    '''(internal) Float value from 0 to 1, used to animate the background when
    the user touches the item.

    :attr:`selected_alpha` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 0.
    '''

    __events__ = ('on_release', )

    def __init__(self, **kwargs):
        super(BusKillSettingItem, self).__init__(**kwargs)
        self.value = self.panel.get_value(self.section, self.key)
        print( "key:|" +str(self.key)+ "|" )
        print( "value:|" +str(self.value)+ "|" )

    def add_widget(self, *largs):
        if self.content is None:
            return super(BusKillSettingItem, self).add_widget(*largs)
        return self.content.add_widget(*largs)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        if self.disabled:
            return
        touch.grab(self)
        self.selected_alpha = 1
        return super(BusKillSettingItem, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.dispatch('on_release')
            Animation(selected_alpha=0, d=.25, t='out_quad').start(self)
            return True
        return super(BusKillSettingItem, self).on_touch_up(touch)

    def on_release(self):
        pass

    def on_value(self, instance, value):
        if not self.section or not self.key:
            return
        # get current value in config
        panel = self.panel
        if not isinstance(value, string_types):
            value = str(value)
        panel.set_value(self.section, self.key, value)

# TODO: actually define a complex option here
class BusKillSettingComplexOptions(BusKillSettingItem):
	icon = ObjectProperty(None)
	'''Implementation of an option list on top of a :class:`SettingItem`.
	It is visualized with a :class:`~kivy.uix.label.Label` widget that, when
	clicked, will open a :class:`~kivy.uix.popup.Popup` with a
	list of options from which the user can select.
	'''

	options = ListProperty([])
	options_long = ListProperty([])
	options_icons = ListProperty([])
	confirmation = ListProperty([])
	'''List of all availables options. This must be a list of "string" items.
	Otherwise, it will crash. :)

	:attr:`options` is a :class:`~kivy.properties.ListProperty` and defaults
	to [].
	'''

	popup = ObjectProperty(None, allownone=True)
	'''(internal) Used to store the current popup when it is shown.

	:attr:`popup` is an :class:`~kivy.properties.ObjectProperty` and defaults
	to None.
	'''

	def __init__(self, **kwargs):
		print( "called BusKillSettingComplexOptions.__init__()" )
#		print( "dir(kwargs):|" +str(dir(kwargs))+ "|" )
#		print( "panel:|" +str(self.panel)+ "|" )
#		print( "options_long:|" +str(self.options_long)+ "|" )
		super(BusKillSettingComplexOptions, self).__init__(**kwargs)
		self.value = self.panel.get_value(self.section, self.key)
#		print( "options_long:|" +str(self.options_long)+ "|" )
#		print( "confirmation:|" +str(self.confirmation)+ "|" )
#		print( "self:|" +str(self)+ "|" )
#		print( "self.parent:|" +str(self.parent)+ "|" )
		#print( "self.get_parent:|" +str(self.get_parent())+ "|" )
#		print( "self.get_root_window():|" +str(self.get_root_window())+ "|" )
		#print( "self.context:|" +str(self.context)+ "|" )
#		print( "self.children:|" +str(self.children)+ "|" )
#		print( "self.walk():|" +str([widget for widget in self.walk()])+ "|" )
#		print( "dir(self):|" +str(dir(self))+ "|\n" )

	def on_panel(self, instance, value):
		print( "entered on_panel()" )
		if value is None:
			return
		self.fbind('on_release', self._choose_settings_screen)

#		if self.icon is None:
#			self.icon = '\ue256'
#			print( "self:|" +str(self)+ "|" )
#			print( "self.parent:|" +str(self.parent)+ "|" )
#			print( "self.children:|" +str(self.children)+ "|" )
#			print( "self.walk():|" +str([widget for widget in self.walk()])+ "|" )
#			print( "dir(self):|" +str(dir(self))+ "|\n" )

	def _set_option(self, instance):
		self.value = instance.text
		self.popup.dismiss()

	def _choose_settings_screen(self, instance):
		print( "he done clicked it" )

		manager = get_screen_manager(self)
		print( "manager:|" +str(manager)+ "|" )
		print( "manager.current:|" +str(manager.current)+ "|" )
		print( "dir(manager):|" +str(dir(manager))+ "|\n" )
		print( App.get_running_app() )
		print( str(App.get_application_name(self)) )

		# create a new screen just for choosing the value of this setting, and name
		# this new screen "setting_<key>" 
		screen_name = 'setting_' +self.key
		setting_screen = BusKillSettingsComplexOptionsScreen(
		 name = screen_name
		)
		
		setting_screen.set_help_msg( self.desc )

		# set the color of the actionbar in this screen equal to whatever our
		# setting's screen actionbar is set to (eg blue or red)
		setting_screen.actionview.background_color = manager.current_screen.actionview.background_color

		# make the text in the actionbar match the 'title' for the setting as it's
		# defined in the settings json file
		setting_screen.set_actionbar_title( self.title )
		print( "setting_screen:|" +str(setting_screen)+ "|" )

#		grid_layout = GridLayout( cols=1 )	
#		float_layout = FloatLayout()	
#		grid_layout.add_widget( float_layout )
#
#		label = Label( text="Title\n[size=13sp][color=999999]And the subtitle here[/color][/size]" )
#		label.markup = True
#		float_layout.add_widget( label )
#		float_layout.height = label.texture_size[1] + dp(10)
#
#		setting_screen.content.add_widget( grid_layout )

		for title, desc, confirmation, icon in zip(self.options, self.options_long, self.confirmation, self.options_icons):
			print( "option_title:|" +str(title)+ "|" )
			print( "option_desc:|" +str(desc)+ "|" )
			print( "option_confirmation:|" +str(confirmation)+ "|" )
			print( "option_icon:|" +str(icon)+ "|" )
			option_item = BusKillOptionItem( title, desc, confirmation, icon, self, manager )
			setting_screen.content.add_widget( option_item )

		main_screen = manager.get_screen('main')
		print( "main_screen:|" +str(main_screen)+ "|" )
		print( "main_screen.properties:|" +str(main_screen.properties)+ "|" )
		print( "main_screen.ids:|" +str(main_screen.ids)+ "|" )
		print( "main_screen.actionbar:|" +str(main_screen.actionbar)+ "|" )
		print( "main_screen.actionview:|" +str(main_screen.actionview)+ "|" )
		print( "main_screen.actionview.background_color:|" +str(main_screen.actionview.background_color)+ "|" )
		print( "dir(main_screen):|" +str(dir(main_screen))+ "|" )

#			# set the actionview of every actionbar of every screen to red
#			for screen in self.manager.screens:
#				for child in screen.actionbar.children:
#					if type(child) == ActionView:
#						child.background_color = self.color_red

		print( "self:|" +str(self)+ "|" )
		print( "self.key:|" +str(self.key)+ "|" )
		print( "self.value:|" +str(self.value)+ "|" )
		print( "self.parent:|" +str(self.parent)+ "|" )
		print( "self.parent.parent:|" +str(self.parent.parent)+ "|" )
		print( "self.parent.parent.parent:|" +str(self.parent.parent.parent)+ "|" )
		print( "self.parent.parent.parent.parent:|" +str(self.parent.parent.parent.parent)+ "|" )
		print( "self.parent.parent.parent.parent.parent:|" +str(self.parent.parent.parent.parent.parent)+ "|" )
		print( "self.parent.parent.parent.parent.parent.parent:|" +str(self.parent.parent.parent.parent.parent.parent)+ "|" )
		#print( str(self.parent()) )
		manager.add_widget( setting_screen )
		#manager.switch_to( newScreen )
		manager.transition.direction = 'left'
		manager.current = screen_name

	def _create_popup(self, instance):
		print( "entered _create_popup()" )
		print( "self.popup:|" +str(self.popup)+ "|" )
		if self.popup:
		   self.popup.dismiss()
		# create the popup
		content = BoxLayout(orientation='vertical', spacing='5dp')
		popup_width = min(0.95 * Window.width, dp(500))
		self.popup = popup = Popup(
			content=content, title=self.title, size_hint=(None, None),
			size=(popup_width, '400dp'))
		popup.height = len(self.options) * dp(55) + dp(150)

		# add all the options
		content.add_widget(Widget(size_hint_y=None, height=1))
		uid = str(self.uid)
		#for option in self.options:
		for option_long in self.options_long:
			state = 'down' if option_long == self.value else 'normal'
			btn = ToggleButton(text=option_long, state=state, group=uid)
			btn.bind(on_release=self._set_option)
			content.add_widget(btn)

		# finally, add a cancel button to return on the previous panel
		content.add_widget(SettingSpacer())
		btn = Button(text='Cancel', size_hint_y=None, height=dp(50))
		btn.bind(on_release=popup.dismiss)
		content.add_widget(btn)

		# and open the popup !
		print( "popup:|" +str(popup)+ "|" )
		print( "popup.parent:|" +str(popup.parent)+ "|" )
		print( "popup.get_parent_window():|" +str(popup.get_parent_window())+ "|" )
		print( "popup.get_root_window():|" +str(popup.get_root_window())+ "|" )
		print( "popup._context:|" +str(popup._context)+ "|" )
		print( "popup.__dict__.items():|" +str(popup.__dict__.items())+ "|" )
		print( "popup._trigger_layout:|" +str(popup._trigger_layout)+ "|" )
		print( "popup.canvas:|" +str(popup.canvas)+ "|" )
		print( "popup._proxy_ref:|" +str(popup._proxy_ref)+ "|" )
		print( "dir(popup):|" +str(dir(popup))+ "|\n" )

		print( "popup.canvas:|" +str(popup.canvas)+ "|" )
		print( "popup.canvas.children:|" +str(popup.canvas.children)+ "|" )
		print( "popup.canvas.before:|" +str(popup.canvas.before)+ "|" )
		print( "popup.canvas.after:|" +str(popup.canvas.after)+ "|" )
		print( "dir(popup.canvas):|" +str(dir(popup.canvas))+ "|\n" )

		popup.open()

class BusKillSettingsContentPanel( kivy.uix.settings.ContentPanel ):
	pass

class BusKillInterfaceWithNoMenu(BusKillSettingsContentPanel):
	pass

class BusKillSettings(kivy.uix.settings.Settings):

	def __init__(self, *args, **kargs):
  		super(BusKillSettings, self).__init__(*args, **kargs)
  		super(BusKillSettings, self).register_type('complex-options', BusKillSettingComplexOptions)

class BusKillSettingsWithNoMenu(BusKillSettings):

	def __init__(self, *args, **kwargs):
		self.fucker='horse'
		self.interface_cls = BusKillInterfaceWithNoMenu
		print( "interface_cls:|" +str(self.interface_cls)+ "|" )
		print( "interface:|" +str(self.interface)+ "|" )
		super(BusKillSettingsWithNoMenu,self).__init__( *args, **kwargs )
		print( "interface_cls:|" +str(self.interface_cls)+ "|" )
		print( "interface:|" +str(self.interface)+ "|" )
#		self.interface_cls = BusKillInterfaceWithNoMenu
#		self.interface = BusKillInterfaceWithNoMenu()
		print( "interface_cls:|" +str(self.interface_cls)+ "|" )
		print( "interface:|" +str(self.interface)+ "|" )
		#self.interface_cls = BusKillInterfaceWithNoMenu

class BusKillSettingsComplexOptionsScreen(Screen):

	actionview = ObjectProperty(None)
	settings_content = ObjectProperty(None)
	actionbar_title = ObjectProperty(None)
	help_msg = ObjectProperty(None)

	def set_help_msg(self, new_help_msg ):
		self.help_msg = new_help_msg

	def set_actionbar_title(self, new_title):
		self.actionbar_title = new_title

	def on_pre_enter(self, *args):

		msg = "DEBUG: User switched to 'BusKillSettingsComplexOptionsScreen' screen"
		print( msg ); logger.debug( msg )

		# set the bk object to the BusKillApp's bk object
		# note we can't set this in __init__() because that's too early. the
		# 'root_app' instance field is manually set by the BusKillApp object
		# after this Screen instances is created but before it's added with
		# add_widget()
		#self.bk = self.root_app.bk

		# the "main" screen
		self.main_screen = self.manager.get_screen('main')

		# close the navigation drawer on the main screen
		#self.main_screen.nav_drawer.toggle_state()

		# we steal (reuse) the instance field referencing the "modal dialog" from
		# the "main" screen
		self.dialog = self.main_screen.dialog

	def show_help( self ):

		self.dialog = DialogConfirmation(
		 #title = '[font=mdicons][size=31]\ue002\ue000\ue645\ue160\ue99a\ue82a\uf22f[/size][/font] Debug Log',
		 title = '[font=mdicons][size=30]\ue88f[/size][/font] ' + str(self.actionbar_title),
		 body = str(self.help_msg),
		 button = "",
		 continue_function=None
		)
		self.dialog.b_cancel.text = "OK"
		self.dialog.open()

class BusKillSettingsScreen(Screen):

	actionview = ObjectProperty(None)
	settings_content = ObjectProperty(None)

	def __init__(self, **kwargs):

		print( "called BusKillSettingsScreen.__init__()" )
		super(BusKillSettingsScreen, self).__init__(**kwargs)
		print( "manager:|" +str(self.manager)+ "|" )

	def on_pre_enter(self, *args):

		msg = "DEBUG: User switched to 'Settings' screen"
		print( msg ); logger.debug( msg )

		print( "manager:|" +str(self.manager)+ "|" )

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

			#self.root_app.settings_cls = BusKillSettingsWithNoMenu
			#print( "interface_cls:|" +str(self.root_app.settings.interface_cls)+ "|" )
			#s = self.root_app.settings_cls()
			s = BusKillSettingsWithNoMenu()
			print( "interface:|" +str(s.interface)+ "|" )
			#self.root_app.build_settings(s)

			s.root_app = self.root_app

#			print( "adding json panel" )
			s.add_json_panel( 'buskill', Config, os.path.join(self.bk.SRC_DIR, 'packages', 'buskill', 'settings_buskill.json') )
#			print( "interface:|" +str(s.interface)+ "|" )

#			print( "s:|" +str(s)+ "|" )
#			print( "s.parent:|" +str(s.parent)+ "|" )
#			print( "s.root_app:|" +str(s.root_app)+ "|" )
#			print( "s.root_app.manager:|" +str(s.root_app.manager)+ "|" )
#			print( "s.get_root_window():|" +str(s.get_root_window())+ "|" )
#			print( "s.get_parent_window():|" +str(s.get_parent_window())+ "|" )
#			print( "s.get_window_matrix():|" +str(s.get_window_matrix())+ "|" )
#			print( "s.children:|" +str(s.children)+ "|" )
#			print( "s.walk():|" +str([widget for widget in s.interface.walk()])+ "|" )
#			print( "dir(s):|" +str(dir(s))+ "|\n" )
#
#			print( "s.interface:|" +str(s.interface)+ "|" )
#			print( "s.interface.panels:|" +str(s.interface.panels)+ "|" )
#			print( "s.interface.current_panel:|" +str(s.interface.current_panel)+ "|" )
#			print( "s.interface.children:|" +str(s.interface.children)+ "|" )
#			print( "s.interface.walk():|" +str([widget for widget in s.interface.walk()])+ "|" )
#			print( "dir(s.interface):|" +str(dir(s.interface))+ "|\n" )
#
#			print( "s.interface.current_panel:|" +str(s.interface.current_panel)+ "|" )
#			print( "s.interface.current_panel.children:|" +str(s.interface.current_panel.children)+ "|" )
#			print( "s.interface.current_panel.walk():|" +str([widget for widget in s.interface.current_panel.walk()])+ "|" )
#			print( "dir(s.interface.current_panel):|" +str(dir(s.interface.current_panel))+ "|\n" )
#
#			print( "s.interface_cls:|" +str(s.interface_cls)+ "|" )
#			print( "s.interface_cls.children:|" +str(s.interface_cls.children)+ "|" )
#			print( "dir(s.interface_cls):|" +str(dir(s.interface_cls))+ "|\n" )
#
#			print( "s.interface.current_panel.someChild:|" +str(s.interface.current_panel.children[0])+ "|" )
			complex_option = s.interface.current_panel.children[0]
#			print( "complex_option:|" +str(complex_option)+ "|" )
#			print( "complex_option.icon:|" +str(complex_option.icon)+ "|" )
#			print( "complex_option.children:|" +str(complex_option.children)+ "|" )
#			print( "complex_option.ids:|" +str(complex_option.ids)+ "|" )
##			print( "complex_option.on_panel:|" +str(complex_option.on_panel)+ "|" )
##			print( "complex_option.key:|" +str(complex_option.key)+ "|" )
##			print( "complex_option.value:|" +str(complex_option.value)+ "|" )
##			print( "complex_option.options:|" +str(complex_option.options)+ "|" )
##			print( "complex_option.popup:|" +str(complex_option.popup)+ "|" )
##			print( "complex_option.section:|" +str(complex_option.section)+ "|" )
##			print( "complex_option.title:|" +str(complex_option.title)+ "|" )
#			print( "complex_option.walk():|" +str([widget for widget in complex_option.walk()])+ "|" )
#			print( "dir(complex_option):|" +str(dir(complex_option))+ "|\n" )
##			s.interface.current_panel.set_value( complex_option.section, complex_option.key, complex_option.value )

			complex_option_key_label = complex_option.children[0].children[1]
			complex_option_value_label = complex_option.children[0].children[0]

#			print( "complex_option_key_label.text:|" +str(complex_option_key_label.text)+ "|" )
#			print( "complex_option_key_label.size:|" +str(complex_option_key_label.size)+ "|" )
#			print( "complex_option_key_label.texture_size:|" +str(complex_option_key_label.texture_size)+ "|" )
#			print( "complex_option_key_label.__dict__.items():|" +str(complex_option_key_label.__dict__.items())+ "|" )
#
#			print( "complex_option_value_label.text:|" +str(complex_option_value_label.text)+ "|" )
#
##			print( "complex_option.content:|" +str(complex_option.content)+ "|" )
##			print( "complex_option.content.children:|" +str(complex_option.content.children)+ "|" )
#			print( "dir(complex_option.content):|" +str(dir(complex_option.content))+ "|\n" )
			#complex_option.add_widget( Label(text='hayy') )
			#complex_option.add_widget( Label(text='hayy2') )

			# for some reason the settings widget automatically includes our
			# ActionBar, such that if we don't remove it before adding the settings
			# widget, we end-up with two action bars. this loop just finds the
			# BoxLayout inside the settings widget (which contains the redundant
			# ActionBar) and removes it
# TODO: remove this section if it's not needed anymore
#			for child in s.children:
#				if type(child) == BoxLayout:
#					s.remove_widget(child) 

			#print( "s.child:|" +str(s.children[0].children[0].children[0].children[0].children)+ "|" )
#			print( str( type(s) ) )
#			print( str( s.children ) )
#			print( str( s.children[0].children ) )
#			print( str( s.children[0].children[0].children ) )
#			print( str( s.children[0].children[0].children[0].children ) )
#			print( "SettingOptions: " +str( s.children[0].children[0].children[0].children[0].children ) )
#			print( "\t" + str( s.children[0].children[0].children[0].children[0].children[0].children ) )
#			print( "\tBoxLayout: " + str( s.children[0].children[0].children[0].children[0].children[0].children[0].children ) )
#			print( "\t\t" + str( s.children[0].children[0].children[0].children[0].children[0].children[0].children[0].children ) )
#			print( "\tLabel: " + str( s.children[0].children[0].children[0].children[0].children[0].children[1].children ) )
#			print( "Label: " +str( s.children[0].children[0].children[0].children[1].children ) )
			#print( str( s.children[0].children[0].children[0] ) )
			#print( str( s.children[0].children[0].children[0].children[0] ) )
			#print( str( s.children[0].children[0].children[0].children[1] ) )
			#print( str( s.children[0].children[0].children[0].children[1] ) )
#			print( "\n***\n" )
#			s.children[0].children[0].children[0].remove_widget( s.children[0].children[0].children[0].children[1] )
#			print( "s.child:|" +str(s.children[0].children[0].children[0].children[0].children)+ "|" )

			#s.remove_widget( s.children[0].children[1] )
			#s.interface.current_panel.title = None
#			for child in s.interface.current_panel.children:
#				if type(child) == Label:
#					s.interface.current_panel.remove_widget(child)

			self.settings_content.add_widget( s )

			s.interface.current_panel.set_value( complex_option.section, complex_option.key, complex_option.value )

	def on_pre_leave(self):
		# update runtime 'bk' instance with any settings changes, as needed
		print( "LEAVING THE SETTINGS SCREEN" )

		self.rearm_if_required()

	def reset_defaults(self):

		msg = "Are you sure you want to reset all your settings back to defaults?"

		self.dialog = DialogConfirmation(
		 title = '[font=mdicons][size=31]\ue002[/size][/font] Warning',
		 body = msg,
		 button='Erase Settings',
		 continue_function=self.reset_defaults2
		)
		self.dialog.b_cancel.text = "Cancel"
		#self.dialog.l_body.bind( on_ref_press=self.ref_press )
		self.dialog.open()

	def reset_defaults2(self):

		# close the dialog if it's already opened
		if self.dialog != None:
			self.dialog.dismiss()

		print( "Erase settings!" )
		for key, value in Config.defaults():
			print(key, value)
		print( Config.sections() )

		# delete all the options saved to the config file
		for key in Config['buskill']:
			Config.remove_option( 'buskill', key )
		Config.write()

#		print( dir(self) )
#		print( dir(self.root_app) )
		self.root_app.build_config(Config)

		self.settings_content = ObjectProperty(None)
		self.__init__()
		print( "self.dialog1:|" +str(self.dialog)+ "|" )

		# TODO: fix the extra dialog
		new_trigger = Config.get('buskill', 'trigger')
		print( 'self.bk.trigger:|' +str(self.bk.trigger) + '|' )
		print( 'new_trigger:|' +str(new_trigger) + '|' )
		#self.on_pre_leave()
		print( "self.dialog2:|" +str(self.dialog)+ "|" )

		self.on_pre_enter()
		print( "self.dialog3:|" +str(self.dialog)+ "|" )

		# TODO: also need to "reset" the sub-screens

		#main_screen = self.manager.get_screen('main')
		#self.manager.switch_to(main_screen)
		#settings_screen = self.manager.get_screen('settings')
		#self.manager.switch_to(settings_screen)

	def rearm_if_required(self):

		# this changes to true if we have to disarm & arm BusKill again i norder to
		# apply the settings that the user changed
		rearm_required = False

		# trigger
		new_trigger = Config.get('buskill', 'trigger')
		print( 'self.bk.trigger:|' +str(self.bk.trigger) + '|' )
		print( 'new_trigger:|' +str(new_trigger) + '|' )

		# was the trigger just changed by the user?
		if self.bk.trigger != new_trigger:
			# the trigger was changed; update the runtime bk instance
			self.bk.trigger = new_trigger

			# is BusKill currently armed?
			if self.bk.is_armed == True:
				# buskill is currently armed; rearming is required to apply the change
				rearm_required = True

		# is it necessary to disarm and arm BusKill in order to apply the user's
		# changes to BusKill's settings?
		if rearm_required:

			msg = "You've made changes to your settings that require disarming & arming again to apply."
			self.dialog = DialogConfirmation(
			 title = '[font=mdicons][size=30]\ue92f[/size][/font]  Apply Changes?',
			 body = msg,
			 button='Disarm & Arm Now',
			 continue_function = self.rearm
			)
			self.dialog.open()

	def rearm(self):

		print( "self.dialog4:|" +str(self.dialog)+ "|" )

		# close the dialog if it's already opened
		if self.dialog != None:
			self.dialog.dismiss()

		# turn it off and on again
		self.main_screen.toggle_buskill()
		self.main_screen.toggle_buskill()

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
		 'trigger': 'lock-screen',
		 'drive': 'all',
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
				print( "adding screen:|" +str(screen)+ "|" )

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
