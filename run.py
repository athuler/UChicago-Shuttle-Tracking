from importlib import reload
import uchicagoShuttleTracking
import sys


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