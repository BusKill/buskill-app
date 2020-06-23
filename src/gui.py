import kivy
#kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label

class BusKill(App):

	def build(self):

		return Label(
		 text = "Welcome to the BusKill App!"
		)

BusKill().run()

