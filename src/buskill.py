def init():
	global buskill_is_armed
	buskill_is_armed = False

def isArmed():
	return buskill_is_armed

def toggleBusKill():

	if isArmed():
		busKill_is_armed = False
	else:
		buskill_is_armed = True
