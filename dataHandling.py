import json
import geopy.distance
import vars
from datetime import datetime


def handleNewWsMessage(wsapp, message):
	try:
		message = json.loads(str(message))
		
		
		
		# Handle Bus Data
		if(message["busId"] not in vars.currentBuses):
			vars.currentBuses[message["busId"]] = vars.Bus(message["busId"])
		
		# Update Passenger Load
		vars.currentBuses[message["busId"]].pax = message["paxLoad"]
		
		# Move Old Coordinates
		vars.currentBuses[message["busId"]].lastLat = vars.currentBuses[message["busId"]].lat
		vars.currentBuses[message["busId"]].lastLon = vars.currentBuses[message["busId"]].lon
		
		# Add New Coordinates
		vars.currentBuses[message["busId"]].lat = message["latitude"]
		vars.currentBuses[message["busId"]].lon = message["longitude"]
		
		
		# Update Ping
		vars.currentBuses[message["busId"]].last_ping = datetime.now()
		
		# Get Closest Stop
		try:
			closestStop, stopDistance = vars.currentBuses[message["busId"]].getClosestStop()
		except Exception as e:
			closestStop, stopDistance = None, None
			vars.errors.append("->Error Getting Closest Stop: " + str(e))
		
		
		if(vars.currentBuses[message["busId"]].paxBeforeArrival == None):
			# Record passenger count before next stop
			vars.currentBuses[message["busId"]].paxBeforeArrival = vars.currentBuses[message["busId"]].pax
		
		
		if(closestStop == None):
			# Bus Is Not At A Stop
			
			
			if(vars.currentBuses[message["busId"]].atStop == True):
				# Bus Was At A Stop
				# But Not Anymore
				vars.currentBuses[message["busId"]].recordStopEvent()
				# Record passenger count before next stop
				vars.currentBuses[message["busId"]].paxBeforeArrival = vars.currentBuses[message["busId"]].pax
				
			# Set Bus Status
			vars.currentBuses[message["busId"]].status = "Traveling"
			vars.currentBuses[message["busId"]].atStop = False
			displayMsgStop = ""
			
			
			
			
			
		elif(
			vars.currentBuses[message["busId"]].recentStop != None and
			closestStop.id == vars.currentBuses[message["busId"]].recentStop.id
		):
			# Bus Is At The Same Stop
			
			vars.currentBuses[message["busId"]].atStop = True
			displayMsgStop = "Stop: " + str(closestStop.name) + " (same)"
		
		
		else:
			# Bus Is At A New Stop
			
			
			
			if(vars.currentBuses[message["busId"]].atStop == True):
				# Bus Was At A Stop
				# And Now At A Different One
				
				# Trigger Stop Event
				vars.currentBuses[message["busId"]].recordStopEvent()
				
				# Record passenger count before next stop
				vars.currentBuses[message["busId"]].paxBeforeArrival = vars.currentBuses[message["busId"]].pax
			
			# Move Old Stop
			vars.currentBuses[message["busId"]].previousStop = vars.currentBuses[message["busId"]].recentStop
			
			# Save Current Stop
			vars.currentBuses[message["busId"]].recentStop = closestStop
			
			# Set Bus Display Status
			vars.currentBuses[message["busId"]].status = "At Stop"
			vars.currentBuses[message["busId"]].atStop = True
			displayMsgStop = "Stop: " + str(closestStop.name) + " (new)"
			
			# Stop Event Timing
			vars.currentBuses[message["busId"]].timeArrivedAtStop = datetime.now()
			
			
		
		# Log New Data
		vars.recentMsgs.append(
			"#"+str(message["busId"])+"\t"+str(message["paxLoad"])+" pax\tLat/Lon: "+str(message["latitude"])+"/"+str(message["longitude"])+"\t"+displayMsgStop
		)
		
	except Exception as e:
		vars.errors.append("->MessageHandlingError:"+str(e))
	

def uploadNumShuttlesData(cnx):
	
	
	NumShuttlesRunning = 0
	NumShuttlesOOS = 0
	NumShuttlesNoGPS = 0
	NumAggPassengers = 0
	RouteBreakdown = {}
	
	for busNum, bus in vars.currentBuses.items():
		
		# Count OOS Buses
		if(bus.routeName == None):
			NumShuttlesOOS += 1
		
		# Count Shuttles W/O GPS
		elif(bus.pax == None):
			NumShuttlesNoGPS += 1
		
		# Count Running Shuttles
		else:
			NumShuttlesRunning += 1
		
		# Count Aggregate Passengers
		if(bus.pax != None):
			NumAggPassengers += bus.pax
			
		# Build Route Breakdown
		if(bus.routeName != None):
			if(bus.routeName not in RouteBreakdown):
				RouteBreakdown[bus.routeName] = 0
			RouteBreakdown[bus.routeName] += 1
	
	
	# Upload Data
	cursor = cnx.cursor()
	insertData = (
		"INSERT INTO NumShuttlesRunning "
		"(NumShuttlesRunning, RouteBreakdown, NumAggPassengers, NumShuttlesOOS, NumShuttlesNoGPS) "
		"VALUES (%(NumShuttlesRunning)s, %(RouteBreakdown)s, %(NumAggPassengers)s, %(NumShuttlesOOS)s, %(NumShuttlesNoGPS)s)"
	)
	data = {
		'NumShuttlesRunning': NumShuttlesRunning,
		'RouteBreakdown': json.dumps(RouteBreakdown),
		'NumAggPassengers': NumAggPassengers,
		'NumShuttlesOOS': NumShuttlesOOS,
		'NumShuttlesNoGPS': NumShuttlesNoGPS,
	}
	cursor.execute(insertData, data)
	cnx.commit()
	cursor.close()
	
	return True


def uploadAlertsData(cnx):
	cursor = cnx.cursor(buffered=True)
	
	# Iterate Through Each Alert
	for alert in vars.systemAlerts:
		
		# Check If Alert Already Exists
		alertCheckQuery = (
			"SELECT * FROM Alerts "
			"WHERE id = %(id)s"
		)
		alertCheckData = {
			'id': alert["id"]
		}
		cursor.execute(alertCheckQuery, alertCheckData)
		
		if(cursor.rowcount == 0):
			
			# Insert New Alert
			
			query = (
				"INSERT INTO Alerts "
				"(id, name, timeCreated, timeFrom, timeTo, htmlContent, routeId, authorId, authorName, timeUpdated, timeLastObserved) "
				"VALUES (%(id)s, %(name)s, %(timeCreated)s, %(timeFrom)s, %(timeTo)s, %(htmlContent)s, %(routeId)s, %(authorId)s, %(authorName)s, %(timeUpdated)s, %(timeLastObserved)s)"
			)
		else:
			
			# Update Alert
			query = (
				"UPDATE Alerts "
				"SET name = %(name)s, timeCreated = %(timeCreated)s, timeFrom = %(timeFrom)s, timeTo = %(timeTo)s, htmlContent = %(htmlContent)s, routeId = %(routeId)s, authorId = %(authorId)s, authorName = %(authorName)s, timeUpdated = %(timeUpdated)s, timeLastObserved = %(timeLastObserved)s "
				"WHERE id = %(id)s"
			)
			
		data = {
			'id': alert["id"],
			'name': alert["name"],
			'timeCreated': alert["created"],
			'timeFrom': alert["from"],
			'timeTo':alert["to"],
			'htmlContent': alert["html"],
			'routeId': alert["routeId"],
			'authorId': alert["authorId"],
			'authorName': alert["author"],
			'timeUpdated': alert["updated"],
			'timeLastObserved': datetime.now(),
		}
		cursor.execute(query, data)
		
		
	
	cnx.commit()
	cursor.close()
	
	return True
	
def uploadStopEvents(cnx):
	
	cursor = cnx.cursor()
	
	for stopEvent in vars.stopEvents:
		if(stopEvent.uploaded == True):
			continue
		
		stopEvent.uploaded = True
		
		# Upload Data
		insertData = (
			"INSERT INTO StopEvents "
			"(stopId, stopName, arrivalTime, departureTime, stopDurationSeconds, routeId, routeName, busId, passengerLoad, nextStopId) "
			"VALUES (%(stopId)s, %(stopName)s, %(arrivalTime)s, %(departureTime)s, %(stopDurationSeconds)s, %(routeId)s, %(routeName)s, %(busId)s, %(passengerLoad)s, %(nextStopId)s)"
		)
		data = {
			'stopId': stopEvent.stop.id,
			'stopName': stopEvent.stop.name,
			'arrivalTime': stopEvent.arrivalTime,
			'departureTime': stopEvent.departureTime,
			'stopDurationSeconds': (stopEvent.departureTime-stopEvent.arrivalTime).seconds,
			'routeId': stopEvent.route,
			'routeName': stopEvent.routeName,
			'busId': stopEvent.busId,
			'passengerLoad': stopEvent.passengerLoad,
			'nextStopId': stopEvent.nextStop[0].id,
		}
		cursor.execute(insertData, data)
		cnx.commit()
	cursor.close()
	