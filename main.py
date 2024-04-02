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
	
	while shutDownEvent.is_set():
		vars.logs.append("Reloading Data...")
		getAllRoutes()
		getAllStops()
		getSystemAlerts()
		getBuses()
		vars.logs.append("Reloaded!")
		
		time.sleep(10)

def display():
	while shutDownEvent.is_set():
		os.system('cls')
		print("========================")
		print("Main Display")
		print("========================")
		
		
		print("Active Buses ("+str(len(vars.currentBuses))+"):")
		
		# No Bus In Service
		if(len(vars.currentBuses) == 0):
			print("No buses in service")
		
		# Display Buses sorted by BusID
		for index, bus in {key: val for key, val in sorted(vars.currentBuses.items(), key = lambda ele: ele[0])}.items():
			
			# Style line
			if(bus.route == None):
				STARTC = vars.bcolors.WARNING
			elif(bus.pax == None):
				STARTC = vars.bcolors.FAIL
			else:
				STARTC = vars.bcolors.OKGREEN
			
			# Compute Time Since Ping
			if(bus.last_ping == None):
				ping = "Never"
			else:
				ping = str(bus.ageSeconds())
			
			
			stopDetected = bus.getClosestStop()
			
			if(stopDetected == None):
				stopString = ""
			else:
				stopString = "At " + str(stopDetected.name)
			
			print(
				STARTC+"#"+str(index)+"\t|",
				bus.pax,"pax | Route #"+str(bus.route)+"-"+str(bus.routeName)+"\t|  "+\
				#"("+str(bus.lat)+"/"+str(bus.lon)+")" +\
				"Age:"+ping+"s"+\
				"\t| "+stopString+\
				vars.bcolors.ENDC
			)
			
			

		print("========================")

		print("Live Data:")
		if(len(vars.recentMsgs) == 0):
			print("No Data")
		for msg in vars.recentMsgs[-3:]:
			print(msg)
		
		print("========================")
		
		print("Recent Logs:")
		for log in vars.logs[-3:]:
			print(log)
		
		print("========================")
		
		print("System Alerts:")
		if(len(vars.systemAlerts) == 0):
			print("No alerts")
		for alert in vars.systemAlerts[-5:]:
			print("->",alert)
		print("========================")
		
		print("Recent Errors:")
		if(len(vars.errors) == 0):
			print("No errors")
		for error in vars.errors[-5:]:
			print(error)
		
		print("========================")
		
		time.sleep(1)

if __name__ == "__main__":
	shutDownEvent = threading.Event()
	shutDownEvent.set()
	
	t1_dataRefresh = threading.Thread(target = refreshData, name="Data Refresh")
	t2_launchWs = threading.Thread(target = launchWS, name="Launch WS")
	t2_launchWs.daemon = True
	t3_display = threading.Thread(target = display, name="Display")
	
	t1_dataRefresh.start()
	t2_launchWs.start()
	t3_display.start()
	
	
	try:
		while 1:
			time.sleep(.1)
	except KeyboardInterrupt:
		print("Shutting Down...")
		shutDownEvent.clear()
		t1_dataRefresh.join()
		t3_display.join()
		print("Shut down!")

