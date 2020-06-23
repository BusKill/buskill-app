#!/usr/bin/env python3.7
################################################################################
# File:    main.py
# Purpose: This is the code to launch the BusKill GUI app
#          For more info, see: https://buskill.in/
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-06-23
# Updated: 2020-06-23
# Version: 0.1
################################################################################

import kivy
#kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout

from kivy.core.window import Window
Window.size = ( 480, 800 )

class MainWindow(GridLayout):

	def toggleBusKill(self):
		print( 'hi' )

class BusKill(App):

	def build(self):
		return MainWindow()


BusKill().run()

