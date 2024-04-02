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
		
		vars.currentBuses[message["busId"]].pax = message["paxLoad"]
		vars.currentBuses[message["busId"]].lat = message["latitude"]
		vars.currentBuses[message["busId"]].lon = message["longitude"]
		vars.currentBuses[message["busId"]].last_ping = datetime.now()
		
		# Get Closest Stop
		closestStop = vars.currentBuses[message["busId"]].getClosestStop()
		if(closestStop != None):
			closestStop = closestStop.name
		
		# Log New Data
		vars.recentMsgs.append(
			"#"+str(message["busId"])+"\t"+str(message["paxLoad"])+" pax\tLat/Lon: "+str(message["latitude"])+"/"+str(message["longitude"])+"\tStop: "+str(closestStop)
		)
		
	except Exception as e:
		vars.errors.append("->MessageHandlingError:"+str(e))
	
	
	