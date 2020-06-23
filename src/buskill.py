import platform

def init():
	global buskill_is_armed
	buskill_is_armed = False

	global ERR_PLATFORM_NOT_SUPPORTED
	ERR_PLATFORM_NOT_SUPPORTED = 'ERROR: Your platform (' +str(platform.system())+ ') is not supported. If you believe this is an error, please file a bug report:\n\nhttps://github.com/BusKill/buskill-app/issues'

def isPlatformSupported():
	if platform.system() in [ 'Linux', 'Windows', 'Darwin' ]:
		return True
	else:
		return False

def isArmed():
	return buskill_is_armed

def toggle():

	if isArmed():

		if platform.system() == 'Linux':
			disarmLin()
		if platform.system() == 'Windows':
			disarmWin()
		if platform.system() == 'Mac':
			disarmMac()

		busKill_is_armed = False

	else:

		if platform.system() == 'Linux':
			armLin()
		if platform.system() == 'Windows':
			armWin()
		if platform.system() == 'Mac':
			armMac()

		buskill_is_armed = True

def armMac():
	print( "placeholder for arming buskill on a mac" )

def armWin():
	print( "placeholder for arming buskill on windows" )

def armLin():
	print( "placeholder for arming buskill on linux" )

def disarmMac():
	print( "placeholder for disarming buskill on a mac" )

def disarmWin():
	print( "placeholder for disarming buskill on windows" )

def disarmLin():
	print( "placeholder for disarming buskill on linux" )
