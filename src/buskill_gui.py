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

import buskill

import kivy
#kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty

from kivy.core.window import Window
Window.size = ( 480, 800 )

class MainWindow(GridLayout):

	buskill.init()

	toggle_btn = ObjectProperty(None)
	status = ObjectProperty(None)

	def toggleBusKill(self):
		if buskill.isArmed():
			self.toggle_btn.text = 'Arm'
			self.status.text = 'BusKill is currently disarmed.'
			self.toggle_btn.background_color = [1,1,1,1]
			buskill.buskill_is_armed = False
		else:
			self.toggle_btn.text = 'Disarm'
			self.status.text = 'BusKill is currently armed.'
			self.toggle_btn.background_color = [1,0,0,1]
			buskill.buskill_is_armed = True

class BusKill(App):

	def build(self):
		return MainWindow()
