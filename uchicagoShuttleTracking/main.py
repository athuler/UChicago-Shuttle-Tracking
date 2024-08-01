# Load Libraries
import os
import time
import threading
import subprocess
from datetime import datetime

from uchicagoShuttleTracking.apiMethods import *
from uchicagoShuttleTracking.dataHandling import *
from uchicagoShuttleTracking.dbMethods import *
import uchicagoShuttleTracking.vars as vars



def refreshData():
	global logs
	
	lastRefreshDataDate = None
	
	while shutDownEvent.is_set():
		try:
			while(
				lastRefreshDataDate != None and
				(datetime.now() - lastRefreshDataDate).seconds < 15
				and shutDownEvent.is_set()
			):
				time.sleep(0.2)
			
			dataSources = [
				getAllRoutes,
				getAllStops,
				getSystemAlerts,
				getBuses,
			]
			for getData in dataSources:
				if(not shutDownEvent.is_set()):
					break
				getData()
			
			lastRefreshDataDate = datetime.now()
			vars.logs.append("Data Reloaded!")
		except Exception as e:
			vars.errors.append("->ErrorRefreshingData: "+str(e))
	
	print("Data Refresh Closed")


def dataUploadThread():
	
	
	# DB Connect
	cnx = dbConnect()
	
	# Declare Dictionaries
	uploadDetails = {}
	
	# Define Data Streams
	uploadDetails["NumShuttles"] = {
		"lastUpload": datetime.now(),
		"freq": 60,
		"func": uploadNumShuttlesData
	}
	uploadDetails["Alerts"] = {
		"lastUpload": datetime.now(),
		"freq": 60,
		"func": uploadAlertsData
	}
	uploadDetails["StopEvents"] = {
		"lastUpload": datetime.now(),
		"freq": 5,
		"func": uploadStopEvents
	}
	
	
	# Iterate Through Data Upload Streams
	while shutDownEvent.is_set() and vars.config["upload_data"]:
		try:
			for key, uploadData in uploadDetails.items():
				
				if(
					uploadData["freq"] == None 
					or
					(datetime.now() - uploadData["lastUpload"]).seconds < uploadData["freq"]
				):
					continue
				
				uploadData["lastUpload"] = datetime.now()
				uploadData["func"](cnx)
				vars.logs.append("Data Uploaded - " + str(key))
			time.sleep(0.25)
		
		
		except Exception as e:
			vars.errors.append("->ErrorUploadingData: " + str(e))
			if(
				cnx is None or
				cnx.is_connected() == False
			):
				vars.logs.append("Reconnecting to DataBase...")
				cnx = dbConnect()
	try:
		cnx.close()
		print("DB Connection Closed")
	except Exception as e:
		print("ERROR Closing Connection")
	

def displayThread():
	while shutDownEvent.is_set():
		refreshDisplay()
		time.sleep(1)


def refreshDisplay():
	os.system('cls')
	print("========================")
	print("UCHICAGO SHUTTLE TRACKER")
	print("========================")
	print(f"Uploading data: {vars.config['upload_data']}")
	print("========================")
	
	
	print("Active Buses ("+str(len(vars.currentBuses))+"):")
	
	# No Bus In Service
	if(len(vars.currentBuses) == 0):
		print("No buses in service")
	
	# Display Buses sorted by BusID
	for index, bus in {key: val for key, val in sorted(vars.currentBuses.items(), key = lambda ele: str(ele[1].route))}.items():
		
		# Style line
		if(
			bus.ageSeconds() != None and
			bus.ageSeconds() > 20
		):
			STARTC = vars.bcolors.FAIL
		elif(bus.route == None):
			STARTC = vars.bcolors.WARNING
		elif(bus.pax == None):
			STARTC = vars.bcolors.FAIL
		
		else:
			STARTC = vars.bcolors.OKGREEN
		
		# Route Name
		displayRouteNameLength = 20
		displayRouteName = str(bus.routeName)
		displayRouteName = ('{:<'+str(displayRouteNameLength)+'}').format(displayRouteName[:displayRouteNameLength])
		if(displayRouteName[-2:] != "  "):
			displayRouteName = displayRouteName[:-2] + ".."
		
		
		# Compute Time Since Ping
		if(bus.last_ping == None):
			ping = "-"
		else:
			ping = str(bus.ageSeconds()) + "s"
		
		
		# Get Bus Status WRT Stop
		stopString = str(bus.status) if bus.status != None else ""
		if(bus.status == "At Stop"):
			# Get Current Stop
			if bus.recentStop != None:
				stopString += ": " + str(bus.recentStop.name)
		elif(bus.status == "Traveling"):
			# Get Next Stop
			nextStop = bus.nextStop()
			if(nextStop != None and nextStop != []):
				stopString += " to: " + str(nextStop[0].name)
				if(len(nextStop) > 1):
					stopString += " (+" + len(nextStop-1) + ")"
			else:
				stopString = ""
		# Trim Stop Name
		stopStringLength = 35
		stopString = ('{:<'+str(stopStringLength)+'}').format(stopString[:stopStringLength])
		if(stopString[-2:] != "  "):
			stopString = stopString[:-2] + ".."
		
		# Process Bus Pax Count
		if(bus.pax != None):
			displayPaxCount = str(bus.pax)
		else:
			displayPaxCount = "-"
			
		
		# Display Bus Info
		print(
			STARTC+\
			displayRouteName +\
			" (#"+str(bus.route) + " / Bus #" + str(index)+")\t" +\
			displayPaxCount + " pax\t" +\
			#"("+str(bus.lat)+"/"+str(bus.lon)+")" +\
			"Age:"+ping+\
			"\t"+stopString+\
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
		print("->",alert["gtfsAlertDescriptionText"])
		#print("->",alert)
	print("========================")
	
	print("Recent Errors:")
	if(len(vars.errors) == 0):
		print("No errors")
	for error in vars.errors[-5:]:
		print(error)
	
	print("========================")
	
	print("Recent Stop Events:")
	if(len(vars.stopEvents) == 0):
		print("No stop events")
	for stopEvent in vars.stopEvents[-3:]:
		print(
			stopEvent.routeName + "\t" + stopEvent.stop.name + "\t" + str((stopEvent.departureTime-stopEvent.arrivalTime).seconds) + "s\t" + str(stopEvent.passengerLoad)
		)
	
	print("========================")
	

def updater(quitOnUpdateAvailable = True):
	installed_version = None
	while shutDownEvent.is_set():
		
		# Update Package With pip
		if installed_version is not None:
			subprocess.run(
			[sys.executable, "-m", "pip", "install", "--upgrade", PIP_URL],
			stdout = subprocess.DEVNULL,
			stderr = subprocess.DEVNULL)
		
		
		# Get Running Vs Installed Versions
		reqs = subprocess.run([sys.executable, '-m', 'pip', 'show', 'Python-Packaging-Test'], capture_output=True).stdout
		for pkg in reqs.split(b"\r\n"):
			if("Version" not in str(pkg)):
				continue
			installed_version = str(pkg).split(": ")[1].replace("'","")
			break
		print(f"Running version: {__version__}")
		print(f"Installed Version: {installed_version}")
		
		# Determine Whether Update is Necessary
		if(__version__ != installed_version and installed_version != None):
			print("UPDATE AVAILABLE")
			
			if quitOnUpdateAvailable:
				shutDownEvent.clear()
		else:
			# No update necessary
			time.sleep(5)
	print("Updater Closed")


def wsManager():
	while shutDownEvent.is_set():
		vars.logs.append("Connecting to WebSocket")
		launchWS()
		vars.logs.append("WebSocket Closed. Reconnecting...")

def main(quitOnUpdateAvailable = False):
	exitCode = 0
	print("Starting up...")
	
	# Set Up Variables
	vars.init()
	
	# Set Up Shutdown Trigger
	global shutDownEvent
	shutDownEvent = threading.Event()
	shutDownEvent.set()
	
	# Prepare Threads
	t1_dataRefresh = threading.Thread(target = refreshData, name="Data Refresh")
	t2_launchWs = threading.Thread(target = wsManager, name="Launch WS")
	t2_launchWs.daemon = True
	t3_display = threading.Thread(target = displayThread, name="Display")
	t4_dataUpload = threading.Thread(target = dataUploadThread, name="Display")
	t5_updater = threading.Thread(target = updater, name="Updater", args = (quitOnUpdateAvailable,))
	
	
	# Launch Threads
	print("Starting Threads...")
	t1_dataRefresh.start()
	t2_launchWs.start()
	t3_display.start()
	t4_dataUpload.start()
	t5_updater.start()
	
		
	while shutDownEvent.is_set():
		try:
			time.sleep(.1)
		except KeyboardInterrupt:
			print("Interrupted")
			exitCode = 1
			shutDownEvent.clear()
			break
	
	# Shut Down Sequence
	print("Shutting Down...")
	t1_dataRefresh.join()
	#t2_launchWs.join()
	t3_display.join()
	t4_dataUpload.join()
	t5_updater.join()
	print("Shut down!")
	return(exitCode)


if __name__ == "__main__":
	main()

