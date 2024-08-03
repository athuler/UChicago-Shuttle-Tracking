from importlib import reload
import uchicagoShuttleTracking
from secrets import *
import sys

global DB_HOST
global DB_NAME
global DB_USER
global DB_PASS

while True:
	
	# Run Application
	exitCode = uchicagoShuttleTracking.run(
		quitOnUpdateAvailable = True # Quits When Update Available & Installed
	)
	
	print(f"Received exit code {exitCode}")
	
	
	if(exitCode == 0):
		# Load Update
		reload(uchicagoShuttleTracking)
		print("Application updated & reloaded!")
	else:
		# Exit Application
		print("Application shut down!")
		break