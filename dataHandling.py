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
		
		# Update Location
		vars.currentBuses[message["busId"]].lat = message["latitude"]
		vars.currentBuses[message["busId"]].lastLat = vars.currentBuses[message["busId"]].lat
		vars.currentBuses[message["busId"]].lon = message["longitude"]
		vars.currentBuses[message["busId"]].lastLon = vars.currentBuses[message["busId"]].lon
		
		# Update Ping
		vars.currentBuses[message["busId"]].last_ping = datetime.now()
		
		# Get Closest Stop
		try:
			closestStop, stopDistance = vars.currentBuses[message["busId"]].getClosestStop()
		except Exception as e:
			vars.errors.append("->Error Getting Closest Stop:" + str(e))
		
		if(closestStop != None):
			vars.currentBuses[message["busId"]].previousStop = vars.currentBuses[message["busId"]].recentStop
			vars.currentBuses[message["busId"]].recentStop = closestStop
			vars.currentBuses[message["busId"]].status = "At Stop"
			displayMsgStop = "Stop: " + str(closestStop.name)
		else:
			vars.currentBuses[message["busId"]].status = "Traveling"
			displayMsgStop = ""
			
		
		# Log New Data
		vars.recentMsgs.append(
			"#"+str(message["busId"])+"\t"+str(message["paxLoad"])+" pax\tLat/Lon: "+str(message["latitude"])+"/"+str(message["longitude"])+"\t"+displayMsgStop
		)
		
	except Exception as e:
		vars.errors.append("->MessageHandlingError:"+str(e))
	

def uploadNumShuttlesData(cnx):
	
	cursor = cnx.cursor()
	insertData = (
		"INSERT INTO NumShuttlesRunning "
		"(NumShuttlesRunning, RouteBreakdown, NumAggPassengers, NumShuttlesOOS) "
		"VALUES (%(NumShuttlesRunning)s, %(RouteBreakdown)s, %(NumAggPassengers)s, %(NumShuttlesOOS)s)"
	)
	data = {
		'NumShuttlesRunning': 0,
		'RouteBreakdown': None,
		'NumAggPassengers': 0,
		'NumShuttlesOOS': 0,
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
				"(id, name, timeCreated, timeFrom, timeTo, htmlContent, routeId, authorId, authorName, timeUpdated) "
				"VALUES (%(id)s, %(name)s, %(timeCreated)s, %(timeFrom)s, %(timeTo)s, %(htmlContent)s, %(routeId)s, %(authorId)s, %(authorName)s, %(timeUpdated)s)"
			)
		else:
			
			# Update Alert
			query = (
				"UPDATE Alerts "
				"SET name = %(name)s, timeCreated = %(timeCreated)s, timeFrom = %(timeFrom)s, timeTo = %(timeTo)s, htmlContent = %(htmlContent)s, routeId = %(routeId)s, authorId = %(authorId)s, authorName = %(authorName)s, timeUpdated = %(timeUpdated)s "
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
		}
		cursor.execute(query, data)
		
		
	
	cnx.commit()
	cursor.close()
	
	return True
	