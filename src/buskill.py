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

def toggleBusKill():

	if isArmed():
		busKill_is_armed = False
	else:
		buskill_is_armed = True

def armMac():
	print( "placeholder for arming buskill on a mac" )

def armWindows():
	print( "placeholder for arming buskill on windows" )

def armLinux():
	print( "placeholder for arming buskill on linux" )
