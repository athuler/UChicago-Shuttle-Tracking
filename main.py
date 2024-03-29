# Load Libraries
import os
import threading
import time
from apiMethods import *
from dataHandling import *
import vars

# Declare Global Variables
vars.init()

def refreshData():
	global logs
	
	while True:
		vars.logs.append("Getting All Routes")
		getAllRoutes()


		vars.logs.append("Getting All Stops")
		getAllStops()


		vars.logs.append("Getting Error Messages")
		getSystemAlerts()


		vars.logs.append("Getting Current Buses")
		getBuses()
		
		time.sleep(15)

def display():
	while True:
		os.system('cls')
		print("========================")
		print("Main Display")
		print("========================")

		
		print("Recent Messages:")
		print(vars.recentMsgs)
		for msg in vars.recentMsgs[-5:]:
			print(msg)
		
		print("========================")
		
		print("Recent Logs:")
		for log in vars.logs[-5:]:
			print(log)
		
		print("========================")
		
		time.sleep(0.5)

if __name__ == "__main__":
	t1_dataRefresh = threading.Thread(target = refreshData, name="Data Refresh")
	t2_launchWs = threading.Thread(target = launchWS, name="Launch WS")
	t3_display = threading.Thread(target = display, name="Display")
	
	t1_dataRefresh.start()
	t2_launchWs.start()
	t3_display.start()

