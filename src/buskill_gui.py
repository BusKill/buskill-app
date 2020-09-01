#!/usr/bin/env python3.7
"""
::

  File:    buskill_gui.py
  Authors: Michael Altfield <michael@buskill.in>
  Created: 2020-06-23
  Updated: 2020-06-23
  Version: 0.1

This is the code to launch the BusKill GUI app

For more info, see: https://buskill.in/
"""

################################################################################
#                                   IMPORTS                                    #
################################################################################

import buskill
import webbrowser

import kivy
#kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ObjectProperty

from kivymd.uix.navigationdrawer import NavigationLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDRaisedButton

from kivy.core.window import Window
Window.size = ( 300, 500 )

from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivymd.app import MDApp
from kivymd.theming import ThemeManager

import logging
logger = logging.getLogger( __name__ )

################################################################################
#                                  SETTINGS                                    #
################################################################################

# n/a

################################################################################
#                                   CLASSES                                    #
################################################################################

class MainWindow(Screen):

	def toggle_buskill( self ):

		buskill.toggle()

		if buskill.isArmed():
			self.toggle_btn.text = 'Disarm'
			self.status.text = 'BusKill is currently armed.'
			self.theme_cls.primary_palette = "Red"
		else:
			self.toggle_btn.text = 'Arm'
			self.status.text = 'BusKill is currently disarmed.'
			self.theme_cls.primary_palette = "Blue"

	def check_for_update1( self ):

		self.nav_drawer.set_state('toggle')

		font_color_hex = kivy.utils.get_hex_from_color( self.theme_cls.text_color )
		msg = "Checking for updates requires internet access.\n\n"
		msg+= "Would you like to check for updates now?"

		self.dialog = MDDialog(
		 type = "custom",
		 title = '[color=' +font_color_hex+ ']Check for Updates?[/color]',
		# TODO: figure out why this text only appears with type=alert (and why
		# the buttons don't call on_release with type=alert)
		 text = '[color=' +font_color_hex+ ']' +msg+ '[/color]',
		 buttons = [
		  MDFlatButton(
		   text = "Cancel",
			on_release = self.close_dialog
		  ),
		  MDRaisedButton(
		   text = "Check Updates",
		   on_release = self.check_for_update2
		  )
		 ]
		)

		self.dialog.size_hint_x = 0.8

		self.dialog.open()

	def close_dialog( self, context ):

		self.dialog.dismiss()

	def check_for_update2( self, context ):

		print( 'ok' )
		print( context )

class CriticalError(BoxLayout):

	msg = ObjectProperty(None)

	def showError( self, msg ):
		self.msg.text = msg

	def fileBugReport( self ):
		# TODO: make this a redirect on buskill.in so old versions aren't tied
		#       to github.com
		webbrowser.open( 'https://docs.buskill.in/buskill-app/en/stable/support.html' )

class BusKill(MDApp):

	def __init__(self, **kwargs):
		self.title = "BusKill"
		self.theme_cls.theme_style = "Dark"
		self.theme_cls.primary_palette = "Blue"
		super().__init__(**kwargs)

	buskill.init()

	def close( self, *args ):
		buskill.close()

	def build(self):

		buskill.init()

		# is the OS that we're running on supported?
		if buskill.isPlatformSupported():

			# yes, this platform is supported; show the main window
			Window.bind( on_request_close = self.close )
			return MainWindow()

		else:
			# the current platform isn't supported; show critical error window

			msg = buskill.ERR_PLATFORM_NOT_SUPPORTED
			print( msg ); logging.error( msg )

			crit = CriticalError()
			crit.showError( buskill.ERR_PLATFORM_NOT_SUPPORTED )
			return crit
