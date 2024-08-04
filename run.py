from importlib import reload
import uchicagoShuttleTracking
from secrets import *
import sys


while True:
	
	# Run Application
	exitCode = uchicagoShuttleTracking.run(
		quitOnUpdateAvailable = True, # Quits When Update Available & Installed
		DB_HOST = DB_HOST,
		DB_NAME = DB_NAME,
		DB_USER = DB_USER,
		DB_PASS = DB_PASS,
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