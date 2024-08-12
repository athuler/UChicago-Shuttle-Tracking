#from importlib import reload
#import uchicagoShuttleTracking
import subprocess
from secret import *
import sys
import time



while True:
	
	# Run Application
	# exitCode = uchicagoShuttleTracking.run(
		# quitOnUpdateAvailable = True, # Quits When Update Available & Installed
		# DB_HOST = DB_HOST,
		# DB_NAME = DB_NAME,
		# DB_USER = DB_USER,
		# DB_PASS = DB_PASS,
	# )
	exitCode = 0
	try:
		# Run Application
		subprocess.run([sys.executable, "-c", f"import uchicagoShuttleTracking; uchicagoShuttleTracking.run(quitOnUpdateAvailable = {True},DB_HOST = '{DB_HOST}', DB_NAME='{DB_NAME}', DB_USER='{DB_USER}', DB_PASS='{DB_PASS}')"])
	except KeyboardInterrupt:
		exitCode = 1
	
	print(f"Received exit code {exitCode}")
	
	
	if(
		exitCode == 0
		#True # DEBUGGING ONLY
	):
		# Load Update
		#reload(uchicagoShuttleTracking)
		
		#reload(sys.modules["uchicagoShuttleTracking"])
		#reload(sys.modules["nicegui"])
		"""
		print(sys.modules)
		for name, module in sys.modules.items():
			if name.startswith("uchicagoShuttleTracking"):
				reload(module)
		# Reload the target module
		reload(sys.modules["uchicagoShuttleTracking"])
		"""

		print("Application updated & reloaded!")
	else:
		# Exit Application
		print("Application shut down!")
		break