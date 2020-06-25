#!/usr/bin/env python3.7
################################################################################
# File:    buskill_gui.py
# Purpose: This is the code to launch the BusKill GUI app
#          For more info, see: https://buskill.in/
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-06-23
# Updated: 2020-06-23
# Version: 0.1
################################################################################

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
from kivy.properties import ObjectProperty

from kivy.core.window import Window
Window.size = ( 480, 800 )

from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

import logging
logger = logging.getLogger( __name__ )

################################################################################
#                                  SETTINGS                                    #
################################################################################

# n/a

################################################################################
#                                   CLASSES                                    #
################################################################################

class MainWindow(BoxLayout):

	toggle_btn = ObjectProperty(None)
	status = ObjectProperty(None)

	def toggleBusKill(self):

		buskill.toggle()

		if buskill.isArmed():
			self.toggle_btn.text = 'Disarm'
			self.status.text = 'BusKill is currently armed.'
			self.toggle_btn.background_color = [1,0,0,1]
		else:
			self.toggle_btn.text = 'Arm'
			self.status.text = 'BusKill is currently disarmed.'
			self.toggle_btn.background_color = [1,1,1,1]

class CriticalError(BoxLayout):

	msg = ObjectProperty(None)

	def showError( self, msg ):
		self.msg.text = msg

	def fileBugReport( self ):
		# TODO: make this a redirect on buskill.in so old versions aren't tied
		#       to github.com
		webbrowser.open( 'https://github.com/BusKill/buskill-app/issues' )

class BusKill(App):

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
