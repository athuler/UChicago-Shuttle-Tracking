# Load Libraries
import os
import sys
import time
import asyncio
import threading
import subprocess
from random import randint
from nicegui import app,ui
from importlib import reload
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
			vars.logs.append(vars.Log("Data Reloaded!"))
		except Exception as e:
			vars.errors.append(vars.Error("->ErrorRefreshingData: "+str(e)))
	
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
				vars.logs.append(vars.Log(f"Data Uploaded - {key}"))
			time.sleep(0.25)
		
		
		except Exception as e:
			vars.errors.append(vars.Error("->ErrorUploadingData: " + str(e)))
			if(
				cnx is None or
				cnx.is_connected() == False
			):
				vars.logs.append(vars.Log("Reconnecting to DataBase..."))
				cnx = dbConnect()
	
	print("Closing DB Connection...")
	try:
		cnx.close()
		print("DB Connection Closed")
	except Exception as e:
		print("ERROR Closing Connection")
	

def displayThread():
	while shutDownEvent.is_set():
		try:
			# Refresh Console
			refreshDisplay()
			
			# Refresh GUI
			ui_shuttles.refresh()
			ui_date.refresh()
			ui_logs()
			ui_errors()
			ui_liveData()
		except Exception as e:
			vars.errors(vars.Error(f"ERROR Displaying Data: {e}"))
			print(f"ERROR Displaying Data: {e}")
		
		# Delay
		time.sleep(1)
	app.shutdown()
	print("Display Closed")


def refreshDisplay():
	os.system('cls||clear')
	print("========================")
	print("UCHICAGO SHUTTLE TRACKER")
	print("========================")
	
	if "upload_data" in vars.config:
		uploadingData = vars.config['upload_data']
	else:
		uploadingData = "Unknown"
	
	print(f"Uploading data: {uploadingData}")
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
		print(msg.message)
	
	print("========================")
	
	print("Recent Logs:")
	for log in vars.logs[-3:]:
		print(log.message)
	
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
		print(error.message)
	
	print("========================")
	
	print("Recent Stop Events:")
	if(len(vars.stopEvents) == 0):
		print("No stop events")
	for stopEvent in vars.stopEvents[-3:]:
		# print(
			# stopEvent.routeName + "\t" + stopEvent.stop.name + "\t" + str((stopEvent.departureTime-stopEvent.arrivalTime).seconds) + "s\t" + str(stopEvent.passengerLoad)
		# )
		print(stopEvent.message)
	
	print("========================")

# START Refreshable GUI Elements

@ui.refreshable
def ui_shuttles() -> None:
	columns = [
		{'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left', 'sortable': True},
		{'name': 'route', 'label': 'Route', 'field': 'route', 'sortable': True},
		{'name': 'busNumber', 'label': 'Bus #', 'field': 'busNumber', 'sortable': True},
		{'name': 'passengers', 'label': 'Passengers', 'field': 'passengers', 'sortable': True},
		{'name': 'age', 'label': 'Age', 'field': 'age', 'sortable': True},
	]
	rows = []
	
	
	# Iterate Through Each Bus
	for index, bus in {key: val for key, val in sorted(vars.currentBuses.items(), key = lambda ele: str(ele[1].route))}.items():
		
		rows.append({
			'name': bus.routeName,
			'route': bus.route,
			'busNumber': index,
			'passengers': bus.pax,
			'age': bus.ageSeconds() if bus.ageSeconds() is not None else 999,
		})
	table = ui.table(
		title = "Live Shuttles",
		columns=columns,
		rows=rows,
		row_key='name'
	)#.classes('w-1/2')
	table.add_slot('body-cell-age', '''
		<q-td key="age" :props="props">
			<q-badge :color="props.value > 15 ? 'red' : 'green'">
				{{ props.value }}
			</q-badge>
		</q-td>
	''')

@ui.refreshable
def ui_date() -> None:
	ui.html(f"<i>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>")

def ui_logs() -> None:
	global uiLogs
	refreshLogs(uiLogs, vars.logs)

def ui_errors() -> None:
	global uiErrors
	refreshLogs(uiErrors, vars.errors)

def ui_liveData() -> None:
	global uiLiveData
	refreshLogs(uiLiveData, vars.recentMsgs)
	
def ui_stopEvents() -> None:
	global uiStopEvents
	refreshLogs(uiStopEvents, vars.stopEvents)
	
def refreshLogs(uiElement, listOfObjects, maxNumOfElements = 30):
	logIndexList = list(range(
		-1,
		max(len(listOfObjects)*(-1),maxNumOfElements*(-1)),
		-1
	))
	for n in logIndexList:
		
		if listOfObjects[n].uiShown:
			continue
		uiElement.push(f">{listOfObjects[n].message}")
		
		listOfObjects[n].uiShown = True
	

# END Refreshable GUI Elements


def updater(quitOnUpdateAvailable = True):
	installed_version = None
	while shutDownEvent.is_set():
		try:
			# Update Package With pip
			if installed_version is not None:
				subprocess.run(
				[sys.executable, "-m", "pip", "install", "--upgrade", PIP_URL],
				stdout = subprocess.DEVNULL,
				stderr = subprocess.DEVNULL)
			
			
			# Get Running Vs Installed Versions
			reqs = subprocess.run([sys.executable, '-m', 'pip', 'show', 'UChicago-Shuttle-Tracking'], capture_output=True).stdout.replace(b"\r",b"")
			for pkg in reqs.split(b"\n"):
				if("Version" not in str(pkg)):
					continue
				installed_version = str(pkg).split(": ")[1].replace("'","")
				break
			vars.logs.append(vars.Log(f"Running version: {__version__}"))
			vars.logs.append(vars.Log(f"Installed Version: {installed_version}"))
			
			# Determine Whether Update is Necessary
			if(__version__ != installed_version and installed_version != None):
				print(f"UPDATE AVAILABLE: {__version__} -> {installed_version}")
				vars.logs.append(vars.Log("UPDATE AVAILABLE"))
				
				if quitOnUpdateAvailable:
					shutDownEvent.clear()
					app.shutdown()
			else:
				# No update necessary
				time.sleep(5)
		except Exception as e:
			vars.errors.append(vars.Error(f"Error in the Updater! {e}"))
			time.sleep(5)
	print("Updater Closed")


def wsManager():
	while shutDownEvent.is_set():
		vars.logs.append(vars.Log("Connecting to WebSocket"))
		launchWS()
		vars.logs.append(vars.Log("WebSocket Closed. Reconnecting..."))


def main(
	quitOnUpdateAvailable = False,
	version = None,
	pipUrl = None,
	DB_HOST = None,
	DB_NAME = None,
	DB_USER = None,
	DB_PASS = None,
):
	global __version__
	__version__ = version
	
	global PIP_URL
	PIP_URL = pipUrl
	
	
	exitCode = 0
	print("Starting up...")
	
	# Set Up Variables
	vars.init(
		DB_HOST,
		DB_NAME,
		DB_USER,
		DB_PASS,
	)
	
	# Set Up GUI
	with ui.column():
		ui.page_title('UChicago Shuttle Tracking')
		ui.dark_mode().enable()
		with ui.column():
			ui.label('UChicago Shuttles').classes('text-h3')
			ui_date()
			with ui.row().classes("w-full"):
				ui_shuttles()
				with ui.column().classes('w-1/4'):
					
					# Alerts
					ui.label('System Alerts')
					global uiAlerts
					uiAlerts = ui.log(max_lines=30).classes("flex-grow h-40").style('white-space: normal') 
					uiAlerts.push("Start of System Alerts")
					uiAlerts.push("This is a very long line ----------- -------- -------- ------------ ----------")
					
					# Live Data
					ui.label('Live Data')
					global uiLiveData
					uiLiveData = ui.log(max_lines=30).classes("flex-grow h-30").style('white-space: normal') 
					uiLiveData.push("-- Start of Live Data --")
					
					# Stop Events
					ui.label('Recent Stop Events')
					global uiStopEvents
					uiStopEvents = ui.log(max_lines=30).classes("flex-grow h-30").style('white-space: normal') 
					uiStopEvents.push("-- Start of Stop Events --")
					
				
				with ui.column().classes('w-1/4'):
					
					# Logs
					ui.label('Logs Here')
					global uiLogs
					uiLogs = ui.log(max_lines=30).classes("flex-grow h-40").style('white-space: normal') 
					uiLogs.push("-- Start of logs --")
					
					# Errors
					ui.label('Errors Here')
					global uiErrors
					uiErrors = ui.log(max_lines=30).classes("flex-grow h-40").style('white-space: normal') 
					uiErrors.push("-- Start of errors --")
	
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
	
		
	#while shutDownEvent.is_set():
	try:
		ui.run(
			show = False,
			reload = False
		)
		print("GUI Closed")
	except KeyboardInterrupt:
		print("Interrupted")
		exitCode = 1
		shutDownEvent.clear()
		#break
	
	# Shut Down Sequence
	print("Shutting Down...")
	app.shutdown()
	t1_dataRefresh.join()
	#t2_launchWs.join()
	t3_display.join()
	t4_dataUpload.join()
	t5_updater.join()
	print("Shut down!")
	return(exitCode)


if __name__ == "__main__":
	main()

